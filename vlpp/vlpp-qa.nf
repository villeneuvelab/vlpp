#!/usr/bin/env nextflow
/*
vim: syntax=groovy
-*- mode: groovy;-*-

Author:
 - Christophe Bedetti <christophe.bedetti@criugm.qc.ca>
*/


/*
 * Parameters validation
 */

if ( params.containsKey('help') ) {
    println """\

    Usage: vlpp-qa
    Options:
        --vlpp_dir
            Directory containing all your subjects directories
        --freesurfer
            Freesurfer directory of your participant
        --participant
            Participant code name
        --tpl
            Default: MNI152_T1_1mm_brain.nii.gz
        --help
            Print vlpp usage
        Nextflow options:
        -resume
            Execute the script using the cached results, useful to continue
            executions that was stopped by an error
        -h, -help
            Print the nextflow usage
    """
    .stripIndent()
    System.exit(0)
}

println("$LOCAL_VL_DIR")
localDir = file "$LOCAL_VL_DIR"
tpl = file localDir / "atlas" / "MNI152_T1_1mm_brain.nii.gz"
suffix = params.suffix


println """\
        ===================
        V L P P - Q A - N F
        -------------------
        template       : ${tpl.baseName}
        ===================
        """
        .stripIndent()


/*
 * SelectFiles
 */

subjects = Channel
    .fromPath( workflow.launchDir / ".." / "sub-*", type: 'dir' )
    .map { it -> [
        "sub": it.baseName,
        "anat": it / "anat" / "${it.baseName}${suffix.anat}",
        "atlas": it / "anat" / "${it.baseName}${suffix.atlas}",
        "brainmask": it / "mask" / "${it.baseName}_roi-brain${suffix.mask}",
        "cerebellumCortex": it / "mask" / "${it.baseName}_roi-cerebellumCortex${suffix.mask}",
        "pet": it / "pet" / "${it.baseName}*space-anat${suffix.pet}",
    ]}
//subjects.into { anat; atlas; pet; petAtlas; dashboard }


/*
 * Mosaics
 */

process mosaics {

    publishDir workflow.launchDir, mode: 'copy', overwrite: true

    //When an input file is not found
    errorStrategy "ignore"

    input:
    val sub from subjects

    output:
    file "data/*_mosaic.jpg"
    file "data/*.json" into participant_json

    script:
    template "qa_mosaics.py"
}

participant_jsons = participant_json.toList()


/*
 * Dashboards
 */

process dashboards {

    publishDir workflow.launchDir, mode: 'copy', overwrite: true

    input:
    val participant_jsons

    output:
    file "*.html"
    file "data/*"

    script:
    template "qa_dashboards.py"
}

/*
 * Assets
 */

process assets {

    publishDir workflow.launchDir, mode: 'copy', overwrite: true

    output:
    file "assets/*/*"

    """
    #!/usr/bin/env python
    # -*- coding: utf-8 -*-
    import os
    from os.path import join as opj
    os.mkdir("assets")
    assetsFiles = [
        ['bootstrap', 'assets', 'css', 'bootstrap.min.css'],
        ['dashboards', 'assets', 'css', 'keen-dashboards.css'],
        ['select2', 'select2.min.css'],
        ['brainsprite.js', 'assets', 'jquery-1.9.1', 'jquery.min.js'],
        ['brainsprite.js', 'assets', 'brainsprite.min.js'],
        ['select2', 'select2.min.js'],
        #['dashboards', 'assets', 'js', 'keen-analytics.js'],
        ]
    for f in assetsFiles:
        source = [os.environ["LOCAL_VL_DIR"]] + f
        try:
            os.mkdir(opj("assets", f[0]))
        except:
            pass
        os.symlink(opj(*source), opj("assets", f[0], f[-1]))
    """
}

/*
{
    "mosaics": {
        "t1": {
        },
        "t1seg": {
            "cmap": "gray"
        },
        "pet": {
        },
        "petwm": {
            "title": "PET and white matter segmentation",
            "notes": "PET image in freesurfer native space with white matter contour"
        },
        "petseg": {
            "title": "PET and aparc+aseg",
            "notes": "PET image in freesurfer native space with aparc+aseg as overlay",
            "cmap": "gray"
        },
        "suvr": {
            "title": "SUVr",
            "notes": "SUVr image in freesurfer native space with cerebellum contour"
        }
    }
}
*/
