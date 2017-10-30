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

        matlabbatch{1}.spm.spatial.normalise.write.subj.def = {'{{anat2tpl}}'};
        matlabbatch{1}.spm.spatial.normalise.write.subj.resample = {'{{img}},1'};
        matlabbatch{1}.spm.spatial.normalise.write.woptions.bb = [-78 -112 -70
                                                                  78 76 85];
        matlabbatch{1}.spm.spatial.normalise.write.woptions.vox = [1 1 1];
        matlabbatch{1}.spm.spatial.normalise.write.woptions.interp = {{interp}};
        matlabbatch{1}.spm.spatial.normalise.write.woptions.prefix = 'w';
        matlabbatch{2}.spm.spatial.coreg.write.ref = {'{{ref}},1'};
        matlabbatch{2}.spm.spatial.coreg.write.source(1) = cfg_dep('Normalise: Write: Normalised Images (Subj 1)', substruct('.','val', '{}',{1}, '.','val', '{}',{1}, '.','val', '{}',{1}, '.','val', '{}',{1}), substruct('()',{1}, '.','files'));
        matlabbatch{2}.spm.spatial.coreg.write.roptions.interp = {{interp}};
        matlabbatch{2}.spm.spatial.coreg.write.roptions.wrap = [0 0 0];
        matlabbatch{2}.spm.spatial.coreg.write.roptions.mask = 0;
        matlabbatch{2}.spm.spatial.coreg.write.roptions.prefix = 'r';


        spm_jobman('run', matlabbatch);

,catch ME,
fprintf(2,'MATLAB code threw an exception:\n');
fprintf(2,'%s\n',ME.message);
if length(ME.stack) ~= 0, fprintf(2,'File:%s\nName:%s\nLine:%d\n',ME.stack.file,ME.stack.name,ME.stack.line);, end;
end;
