#!/usr/bin/env nextflow
/*
vim: syntax=groovy
-*- mode: groovy;-*-

    Villeneuve Laboratory PET Pipeline (VLPP)

    For any bugs or problems found, please contact us at:
      - https://github.com/villeneuvelab/vlpp/issues
*/


/*
 * Parameters validation
 */

// Help
if ( params.containsKey('help') ) {
    println """\
    Execute the vlpp project
    Usage: vlpp --pet <> --freesurfer <> --participant <> [-c <>]
        Options:
        --pet
            Pet file [.mnc, .nii or .nii.gz]
        --freesurfer
            Freesurfer directory of the participant
        --participant
            Participant code name
        --help
            Print vlpp usage
        Nextflow options:
        -c
            Load a configuration file
            Default configuration : launch vlpp-default-cfg
            Example configuration : launch vlpp-example-cfg
            More information: https://www.nextflow.io/docs/latest/config.html
        -resume
            Execute the script using the cached results, useful to continue
            executions that was stopped by an error
        -h, -help
            Print the nextflow usage
    """
    .stripIndent()
    System.exit(0)
}

// Checking mandatory parameters
['pet', 'freesurfer', 'participant'].each {
    if( !params.containsKey(it) ) {
        println "The parameter `${it}` is not set"
        println "`vlpp --help` for vlpp usage"
        println "`vlpp -help` for nextflow usage"
        System.exit(0)
    }
}

// Checking configuration

//tracer
if( config.dataset == "DIAN" ) { config.tracer = "PIB" }
else if( config.tracer ) {}
else if( config.dataset == "PAD" ) {
    if( params.participant[-1] == "2" ) {
        config.tracer = params.participant[-4..-2]
    }
    else { config.tracer = params.participant[-3..-1] }
}


// Channels and pipeline values
//baseSf1 = file "/sf1"
//localDir = baseSf1 / "project" / "yai-974-aa" / "local"
//tpl = localDir / "atlas" / "MNI152_T1_1mm.nii"

participant = params.participant
suffix = config.suffix

petInput = file params.pet

freesurferDir = file params.freesurfer
anatInput = freesurferDir / "mri" / "T1.mgz"
atlasInput = freesurferDir / "mri" / "aparc+aseg.mgz"
nuInput = freesurferDir / "mri" / "nu.mgz"

fsRefList = []
config.fsReferences.each() { k, v -> fsRefList << [k,v] }
fsRefs = Channel.from(fsRefList)

println """\
        =============
        V L P P - N F
        -------------
        PET file     : ${petInput}
        freesurfer   : ${freesurferDir}
        participant  : ${participant}
        dataset      : ${config.dataset}
        tracer       : ${config.tracer}
        ============="""
        .stripIndent()


/*
 *  Preparation
 */

process anatconvert {

    publishDir "anat", mode: 'copy', overwrite: true

    input:
    file img from anatInput

    output:
    file "*" + suffix.anat into anat

    """
    mri_convert -ot nii -i ${img} -o ${participant}${suffix.anat}
    """
}

process nuconvert {

    publishDir "anat", mode: 'copy', overwrite: true

    input:
    file img from nuInput

    output:
    file "*" + suffix.nu into nu

    """
    mri_convert -ot nii -i ${img} -o ${participant}${suffix.nu}
    """
}

process atlasconvert {

    publishDir "anat", mode: 'copy', overwrite: true

    input:
    file img from atlasInput

    output:
    file "*" + suffix.atlas into atlas

    """
    mri_convert -ot nii -i ${img} -o ${participant}${suffix.atlas}
    """
}

process petconvert {

    echo true

    input:
    file img from petInput

    output:
    file "*" + suffix.pet into petnii

    script:
    template "petconvert.py"
}


/*
 *  Realign
 */

realignParams = config.realign
process realign {

    if( realignParams.keepTmp ) {
        publishDir workflow.launchDir, mode: 'copy', overwrite: true
    }
    else {
        publishDir workflow.launchDir, mode: 'copy', overwrite: true, pattern: "transform/*.txt"
    }

    input:
    file pet from petnii
    val dataset from config.dataset

    output:
    file "tmp/*tmp-estimate.*" into petToEstimate
    file "tmp/*time-4070.*" into pet4070ToRegister
    file "tmp/*time-5070.*" into pet5070ToRegister
    file "transform/*"

    script:
    template "realign.py"
}


/*
 * Segmentation
 */

process segmentation {

    publishDir workflow.launchDir, mode: 'copy', overwrite: true, pattern: "*/*gz"

    input:
    file img from nu
    val spmDir from config.spmDir

    output:
    file "mask/*roi-c1" + suffix.mask into gmSpm
    file "mask/*roi-c2" + suffix.mask into wmSpm
    file "mask/*roi-c3" + suffix.mask into csfSpm
    file "mask/*roi-c4" + suffix.mask into boneSpm
    file "mask/*roi-c5" + suffix.mask into softSpm
    file "transform/*"
    file "y_*.nii" into anat2tpl
    file "iy_*.nii" into tpl2anat

    script:
    type = "spm12"
    template "segmentation.py"
}


process segmentation_suit {

    publishDir workflow.launchDir, mode: 'copy', overwrite: true, pattern: "*/*gz"

    input:
    file img from nu
    val spmDir from config.spmDir

    output:
    //file "mask/*roi-c1" + suffix.mask into gmSuit
    //file "mask/*roi-c2" + suffix.mask into wmSuit
    file "suit/*" + suffix.suit into atlasCereb

    script:
    type = "suit"
    template "segmentation.py"
}

process brainmask {

    publishDir "mask", mode: 'copy', overwrite: true

    input:
    file gm from gmSpm
    file wm from wmSpm
    file csf from csfSpm

    output:
    file "*roi-brain" + suffix.mask into brainMask
    file "*roi-gmwm" + suffix.mask into gmwmMask

    """
    brain=${participant}_roi-brain${suffix.mask}
    fslmaths $gm -add $wm -add $csf -fillh -bin \$brain

    gmwm=${participant}_roi-gmwm${suffix.mask}
    fslmaths $gm -thr 0.25 tmp_gm.nii.gz
    fslmaths $wm -thr 0.25 tmp_wm.nii.gz
    fslmaths tmp_gm.nii.gz -add tmp_wm.nii.gz -bin \$gmwm
    """
}


/*
 * Registrations
 */

process estimate_pet2anat {

    publishDir "transform", mode: 'copy', overwrite: true

    // ANTSImageRegistrationOptimizer error
    //https://sourceforge.net/p/advants/discussion/840260/thread/7cf6ba92/
    //Just ignore the error
    errorStrategy "ignore"

    input:
    file anat
    file pet from petToEstimate

    output:
    file "*" + suffix.pet2anat into pet2anat

    script:
    template "estimate_pet2anat.sh"
}

pet2anatPetParams = config.pet2anat.pet
pet2anatCentiloidParams = config.pet2anat.centiloid
process apply_pet2anat {

    echo true
    cache 'deep'
    publishDir workflow.launchDir, mode: 'copy', overwrite: true

    input:
    file pet4070 from pet4070ToRegister
    file pet5070 from pet5070ToRegister
    file anat
    file pet2anat
    file gmwm from gmwmMask
    file brain from brainMask

    output:
    file "pet/*space-anat*" into pet4070InAnat
    file "centiloid/*space-anat*" into pet5070InAnat

    script:
    template "apply_pet2anat.py"
}

process apply_anat2tpl {

    publishDir workflow.launchDir, mode: 'copy', overwrite: true

    input:
    file anat
    file atlas
    file pet4070 from pet4070InAnat
    file pet5070 from pet5070InAnat
    file anat2tpl

    output:
    file "anat/*space-tpl*"
    file "pet/*space-tpl*"
    file "centiloid/*space-tpl*" into pet5070InTpl

    script:
    template "apply_anat2tpl.py"
}


/*
 *  Pickatlas
 */

process pickatlas {

    publishDir "mask", mode: 'copy', overwrite: true

    input:
    file atlas
    set refName, indices from fsRefs

    output:
    file "*" + suffix.mask into refmask

    script:
    template "pickatlas.py"
}


/*
 * Suvr & Centiloid
 */

process suvr_baker {

    publishDir workflow.launchDir, mode: 'copy', overwrite: true

    input:
    val bakerDir from config.bakerDir
    file atlas
    file pet4070 from pet4070InAnat
    file gmSpm
    file wmSpm
    file csfSpm
    file boneSpm
    file softSpm
    file atlasCereb

    output:
    file "baker/*"
    file "stats/*"

    when:
    tracer.matches("TAU")

    script:
    template "suvr_baker.py"
}


process compute_metrics_anat {

    publishDir workflow.launchDir, mode: 'copy', overwrite: true

    input:
    file pet4070 from pet4070InAnat
    file pet5070 from pet5070InAnat
    file refmask
    file atlas

    output:
    file "pet/*"
    file "centiloid/*"
    file "stats/*"

    script:
    template "compute_metrics_anat.py"
}

process compute_metrics_tpl {

    publishDir workflow.launchDir, mode: 'copy', overwrite: true

    input:
    file pet from pet5070InTpl
    val tracer from config.tracer
    val centiloidRoiDir from config.centiloidRoiDir

    output:
    file "centiloid/*"
    file "stats/*"

    when:
    tracer.matches("PIB|NAV")

    script:
    template "compute_metrics_tpl.py"
}

