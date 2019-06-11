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


        addpath('{{bakerDir}}');
        %TAU_PVC_RUNME_Create_ROIs_For_Rousset('{{atlas}}','{{pet}}','{{gmSpm}}','{{wmSpm}}','{{csfSpm}}','{{boneSpm}}','{{softSpm}}','{{atlasCereb}}',[6.5 6.5 7.5]),
        TAU_RUNME_Create_ROIs_For_Rousset('{{atlas}}','{{pet}}','{{gmSpm}}','{{wmSpm}}','{{csfSpm}}','{{boneSpm}}','{{softSpm}}','{{atlasCereb}}',{{scannerResolution}}),



,catch ME,
fprintf(2,'MATLAB code threw an exception:\n');
fprintf(2,'%s\n',ME.message);
if length(ME.stack) ~= 0, fprintf(2,'File:%s\nName:%s\nLine:%d\n',ME.stack.file,ME.stack.name,ME.stack.line);, end;
end;


