import os
import subprocess
from .gslab_builder import GSLabBuilder


def build_latex(target, source, env):
    '''
    Compile a pdf from a LaTeX file

    This function is a SCons builder that compiles a .tex file
    as a pdf and places it at the path specified by target.

    Parameters
    ----------
    target: string or list
        The target of the SCons command. This should be the path
        of the pdf that the builder is instructed to compile.
    source: string or list
        The source of the SCons command. This should
        be the .tex file that the function will compile as a PDF.
    env: SCons construction environment, see SCons user guide 7.2
    '''
    builder_attributes = {
        'name': 'LaTeX',
        'valid_extensions': ['.tex'],
        'exec_opts': '-pdf -interaction=nonstopmode'  # TODO There should be as switch here, based on what the exec is...
    }
    builder = LatexBuilder(target, source, env, **builder_attributes)
    builder.execute_system_call()
    return None

# TODO there's probably an easier way to do all of this, like by rewriting
#  target/source/log paths instead of on a case-by-case basis. But for now this
#  works --- reconsider when finally forking this package.
class LatexBuilder(GSLabBuilder):
    """"""
    def add_call_args(self):
        """"""
        target_name = os.path.splitext(self.target[0])[0]

        if self.env['rel_path'] is True:
            # Hack so I can use Texifier when writing, and SCons for real builds
            # The assumption here is that the chdir attribute is set to the source dir.
            args = '%s -output-directory=%s -bibtex -jobname=%s %s > %s' % (
                self.cl_arg,
                os.path.relpath(
                    path=os.path.dirname(target_name),
                    start=os.path.dirname(self.source_file)
                ),
                os.path.basename(target_name),  # TODO Is this robust to Windows paths?
                os.path.basename(self.source_file),  # TODO Is this robust to Windows paths?
                os.path.relpath(
                    path=os.path.normpath(self.log_file),
                    start=os.path.dirname(self.source_file)
                )
            )
        else:
            target_name = os.path.splitext(self.target[0])[0]
            args = '%s %s %s > %s' % (self.cl_arg, target_name, os.path.normpath(self.source_file), os.path.normpath(self.log_file))
        self.call_args = args
        return None

    def check_targets(self):
        '''
        Check that all elements of the target attribute after executing system call.

        Redefined here to manage the different approach to paths.
        '''
        if self.env['rel_path'] is True:
            missing_targets = [t for t in self.target if not os.path.isfile(os.path.relpath(path=t, start=os.path.dirname(self.source_file)))]
        else:
            missing_targets = [t for t in self.target if not os.path.isfile(t)]
        if missing_targets:
            missing_targets = '\n    '.join(missing_targets)
            message = 'The following target files do not exist after build:\n    %s' % missing_targets
            raise TargetNonexistenceError(message)
        return None

    def timestamp_log(self, start_time, end_time):
        '''
        Adds beginning and ending times to a log file made for system call.
        '''
        if self.env['rel_path'] is True:
            log_path = os.path.relpath(path=self.log_file, start=os.path.dirname(self.source_file))
        else:
            log_path = self.log_file
        with open(log_path, mode = 'r') as f:
            content = f.read()
            f.seek(0, 0)
            builder_log_msg = '*** Builder log created: {%s}\n' \
                              '\n' \
                              '*** Builder log completed: {%s}\n%s' \
                              % (start_time, end_time, content)
        with open(log_path, mode = 'w') as f:
            f.write(builder_log_msg)
        return None
