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



        addpath('{{compat}}');
        matlabbatch{1}.spm.tools.suit.isolate_seg.source = {{'{{'}}'{{anat}},1'{{'}}'}};
        matlabbatch{1}.spm.tools.suit.isolate_seg.bb = [-76 76
                                                        -108 -6
                                                        -70 11];
        matlabbatch{1}.spm.tools.suit.isolate_seg.maskp = 0.2;
        matlabbatch{1}.spm.tools.suit.isolate_seg.keeptempfiles = 1;


        spm_jobman('run', matlabbatch);

,catch ME,
fprintf(2,'MATLAB code threw an exception:\n');
fprintf(2,'%s\n',ME.message);
if length(ME.stack) ~= 0, fprintf(2,'File:%s\nName:%s\nLine:%d\n',ME.stack.file,ME.stack.name,ME.stack.line);, end;
end;

