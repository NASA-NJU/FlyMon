import subprocess
import jinja2
import sys
import functools
import random

class Tester():
    def __init__(self, test_dir, test_file, test_args, out_file):
        self._test_dir = test_dir
        self._test_file = test_file
        self._test_args = test_args
        self._test_name = test_file.replace('.cpp_template', '')
        self._output = out_file
        pass
    
    def generate_codes(self, exec_name=None):
        generated_file = ''
        if exec_name is None:
            generated_file = self._test_dir + '/' + self._test_name + '.cpp'
        else:
            generated_file = self._test_dir + '/' + exec_name + '.cpp'
        env = jinja2.Environment(loader=jinja2.FileSystemLoader(self._test_dir))  
        mdata_template = env.get_template(self._test_file)
        mdata_temp_out = mdata_template.render(self._test_args)
        print("Generating codes...")
        with open(generated_file, 'w') as f:
            f.writelines(mdata_temp_out.encode('raw_unicode_escape'))
            f.close()
        print("Compile codes...")
        # temp_build_dir = 'build_' + self._test_name + '_%d' %(random.randint(1,10000),)
        process_build = subprocess.Popen('cd ./build; cmake ..; make -j2; cd ..; exit 0', shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        for line in iter(process_build.stdout.readline, b''):
            sys.stdout.write(line)
        process_build.wait()
        if process_build.returncode != 0:
            print("Compile Failed! See "+ self._output + ' for detail.')
            exit(1)
        return

    def runTest(self, process_id=0, exec_name=None):
        print("[PID %d]: Test running once!" %(process_id,))
        test_exec = None
        if exec_name is None:
            test_exec = 'bin/'  + '/' + self._test_name
        else:
            test_exec = 'bin/'  + '/' + exec_name
        with open(self._output, 'a') as output: 
            print("Running codes...")
            process_execute = subprocess.Popen(test_exec, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            for line in iter(process_execute.stdout.readline, b''):
                sys.stdout.write(line)
                output.write(line)
            process_execute.wait()
            if process_execute.returncode !=0:
                print("Runtime Failed! See "+ self._output + ' for detail.')
                exit(1)
            print("Test %s done. See %s for detail." % (self._test_name, self._output))
            output.write('====================================================\n')
            output.close()