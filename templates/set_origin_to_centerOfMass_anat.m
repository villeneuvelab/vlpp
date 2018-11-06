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

        % use center-of-mass (COM) to roughly correct for differences in the
        % position between image and template
        % The center of mass is always close to the AC
        %
        % This script comes from VBM8 toolbox, modified by petpve12 toolbox
        % and modified to fit this pipeline

        anat = spm_vol('{{anat}},1');
        nu = spm_vol('{{nu}},1');
        atlas = spm_vol('{{atlas}},1');

        % pre-estimated COM of MNI template
        com_reference = [0 -20 -30];
        % com_reference = [0 -20 -15];% closer to the AC

        fprintf('Setting orig to center-of-mass for %s\n',nu.fname);
        Affine = eye(4);

        vol = spm_read_vols(nu);
        avg = mean(vol(:));
        avg = mean(vol(find(vol>avg)));

        % don't use background values in COM calculation
        [x,y,z] = ind2sub(size(vol),find(vol>avg));
        com = nu.mat(1:3,:)*[mean(x) mean(y) mean(z) 1]';
        com = com';

        M = spm_get_space(nu.fname);
        Affine(1:3,4) = (com - com_reference)';

        spm_get_space(anat.fname,Affine\M);
        spm_get_space(nu.fname,Affine\M);
        spm_get_space(atlas.fname,Affine\M);

,catch ME,
fprintf(2,'MATLAB code threw an exception:\n');
fprintf(2,'%s\n',ME.message);
if length(ME.stack) ~= 0, fprintf(2,'File:%s\nName:%s\nLine:%d\n',ME.stack.file,ME.stack.name,ME.stack.line);, end;
end;


