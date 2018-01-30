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

    Usage: vlpp-qa [-c <>]
    Options:
        --help
            Print vlpp usage
        Nextflow options:
        -c
            Load a configuration file
            Default configuration : look at config/qa.config
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

tpl = file config.tpl
//suffix = config.suffix


println """\
        ===================
        V L P P - Q A - N F
        -------------------
        ===================
        """
        .stripIndent()


/*
 * SelectFiles
 */

Channel
    .fromPath( workflow.launchDir / ".." / "sub-*", type: 'dir' )
    .map { it -> [
        "sub": it.baseName,
        "anat": it / "anat" / "${it.baseName}*T1w.nii.gz",
        "anatTpl": it / "anat" / "${it.baseName}*T1w*space-tpl.nii.gz",
        "atlas": it / "anat" / "${it.baseName}*aparc+aseg.nii.gz",
        "brainmask": it / "mask" / "${it.baseName}*roi-brain*mask.nii.gz",
        "cerebellumCortex": it / "mask" / "${it.baseName}*roi-cerebellumCortex*mask.nii.gz",
        "pet": it / "pet" / "${it.baseName}*space-anat.nii.gz",
        "centiloid": it / "centiloid" / "${it.baseName}*space-tpl.nii.gz",
    ]}.into { subjects_T1w; subjects_tpl }


/*
 * Mosaics
 */

process mosaics_T1w {

    publishDir workflow.launchDir, mode: 'copy', overwrite: true

    //When an input file is not found
    errorStrategy "ignore"

    input:
    val sub from subjects_T1w

    output:
    file "data/*_mosaic.jpg"
    file "data/*.json" into participant_json

    script:
    template "qa_mosaics_T1w.py"
}

process mosaics_tpl {

    publishDir workflow.launchDir, mode: 'copy', overwrite: true

    //When an input file is not found
    errorStrategy "ignore"

    input:
    val sub from subjects_tpl

    output:
    file "data/*_mosaic.jpg"
    file "data/*.json" into participant_json_tpl

    script:
    template "qa_mosaics_tpl.py"
}

participant_jsons = participant_json.toList()
participant_jsons_tpl = participant_json_tpl.toList()


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

    """
    #!/usr/bin/env python
    # -*- coding: utf-8 -*-
    from vlpp.dashboards import anat_dash
    jsonPaths = "${participant_jsons}"[1:-1].split(", ")
    anat_dash(jsonPaths)
    """
}

process dashboards_tpl {

    publishDir workflow.launchDir, mode: 'copy', overwrite: true

    input:
    val participant_jsons_tpl

    output:
    file "*.html"
    file "data/*"

    """
    #!/usr/bin/env python
    # -*- coding: utf-8 -*-
    from vlpp.dashboards import tpl_dash
    jsonPaths = "${participant_jsons_tpl}"[1:-1].split(", ")
    tpl_dash(jsonPaths)
    """
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
