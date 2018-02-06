fprintf(1,'Executing %s at %s:\n',mfilename(),datestr(now));
ver,
try,
        if isempty(which('spm')),
             throw(MException('SPMCheck:NotFound', 'SPM not in matlab path'));
        end
        [name, version] = spm('ver');
        fprintf('SPM version: %s Release: %s\n',name, version);
        fprintf('SPM path: %s\n', which('spm'));
        spm('defaults', 'PET');

        if strcmp(name, 'SPM8') || strcmp(name(1:5), 'SPM12'),
           spm_jobman('initcfg');
           spm_get_defaults('cmdline', 1);
        end



        matlabbatch{1}.spm.tools.suit.isolate.source = {{"{{"}}'{{anat}},1'{{"}}"}};
        matlabbatch{1}.spm.tools.suit.isolate.bb = [-76 76
                                                    -108 -6
                                                    -75 11];
        matlabbatch{1}.spm.tools.suit.isolate.cerebral_range = 3.5;
        matlabbatch{1}.spm.tools.suit.isolate.cerebellar_range = 2.5;

        matlabbatch{2}.spm.tools.suit.normalise.subjN.source = {'c_img.nii,1'};
        matlabbatch{2}.spm.tools.suit.normalise.subjN.mask = {'c_img_pcereb_corr.nii,1'};
        matlabbatch{2}.spm.tools.suit.normalise.subjN.lesion_mask = '';
        matlabbatch{2}.spm.tools.suit.normalise.prefix = 'wsuit_';
        matlabbatch{2}.spm.tools.suit.normalise.template = {'{{spmDir}}/toolbox/suit/templates/SUIT.img'};
        matlabbatch{2}.spm.tools.suit.normalise.template_weight = {'{{spmDir}}/toolbox/suit/templates/SUIT_weight.img'};
        matlabbatch{2}.spm.tools.suit.normalise.param_postfix = '_snc';
        matlabbatch{2}.spm.tools.suit.normalise.smooth_mask = 2;
        matlabbatch{2}.spm.tools.suit.normalise.estimate.smosrc = 2;
        matlabbatch{2}.spm.tools.suit.normalise.estimate.smoref = 0;
        matlabbatch{2}.spm.tools.suit.normalise.estimate.regtype = 'subj';
        matlabbatch{2}.spm.tools.suit.normalise.estimate.cutoff = 10;
        matlabbatch{2}.spm.tools.suit.normalise.estimate.nits = 30;
        matlabbatch{2}.spm.tools.suit.normalise.estimate.reg = 1;
        matlabbatch{2}.spm.tools.suit.normalise.write.preserveN = 0;
        matlabbatch{2}.spm.tools.suit.normalise.write.bb = [-70 -100 -75
                                                            70 -6 11];
        matlabbatch{2}.spm.tools.suit.normalise.write.voxN = [1 1 1];
        matlabbatch{2}.spm.tools.suit.normalise.write.interpN = 1;
        matlabbatch{2}.spm.tools.suit.normalise.write.wrapN = [0 0 0];

        %matlabbatch{3}.spm.tools.suit.reslice_inv.resample = {'{{spmDir}}/toolbox/suit/atlas/SUIT.nii,1'};
        %matlabbatch{3}.spm.tools.suit.reslice_inv.paramfile = {'mc_img_snc.mat'};
        %matlabbatch{3}.spm.tools.suit.reslice_inv.prefix = 'i';
        %matlabbatch{3}.spm.tools.suit.reslice_inv.interp = 3;
        %matlabbatch{3}.spm.tools.suit.reslice_inv.reference = {'img.nii,1'};

        %matlabbatch{4}.spm.tools.suit.reslice_inv.resample = {'{{spmDir}}/toolbox/suit/atlas/Cerebellum-SUIT.nii,1'};
        %matlabbatch{4}.spm.tools.suit.reslice_inv.paramfile = {'mc_img_snc.mat'};
        %matlabbatch{4}.spm.tools.suit.reslice_inv.prefix = 'i';
        %matlabbatch{4}.spm.tools.suit.reslice_inv.interp = 0;
        %matlabbatch{4}.spm.tools.suit.reslice_inv.reference = {'img.nii,1'};

        spm_jobman('run', matlabbatch);

        suit_reslice_inv('{{spmDir}}/toolbox/suit/atlas/SUIT.nii', 'mc_img_snc.mat', 'interp', 3, 'reference', 'img.nii')
        suit_reslice_inv('{{spmDir}}/toolbox/suit/atlas/Cerebellum-SUIT.nii', 'mc_img_snc.mat', 'interp', 0, 'reference', 'img.nii')


,catch ME,
fprintf(2,'MATLAB code threw an exception:\n');
fprintf(2,'%s\n',ME.message);
if length(ME.stack) ~= 0, fprintf(2,'File:%s\nName:%s\nLine:%d\n',ME.stack.file,ME.stack.name,ME.stack.line);, end;
end;

