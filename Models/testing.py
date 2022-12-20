import subprocess
import time
from pathlib import Path
import configparser
import json
import sqlite3


class ErrorTesting(Exception):
    pass


class Testing:
    def testing_module(self, test_info, db, rearg):
        try:
            with sqlite3.connect("dbase.db") as con:
                cur = con.cursor()
                cur.execute(f"UPDATE code_task SET status = 'testing...' WHERE id = '{db}'")
                con.commit()
            compiler = self.compiler(db)
            config = configparser.ConfigParser()  # .ini файлы
            config.read(f'instance/task/{rearg}/config.ini', encoding="utf-8")  # чтение
            test_s = config['Config']['tests']
            limit = config['Config']['time_limit']
            memory = config['Config']['memory_limit']
            checker_ = config['Checker']['checker']
            out_result = {'result_all_info': {
                'all_test': int(test_s),
                'compilation': '',
                'success_test': 0,
                'failed_test': 0,
                'first_failed_test': int(test_s) + 1,
                'bad_time': 0,
                'bad_memory': 0,
                'points': 0
            },
                'testing_result': {}}

            if 'NO COMPILER' != compiler[test_info["lang"]][0][0]:
                with sqlite3.connect("dbase.db") as con:
                    cur = con.cursor()
                    cur.execute(f"UPDATE code_task SET status = 'compilation...' WHERE id = '{db}' ")
                    con.commit()
                compilation = subprocess.Popen(compiler[test_info["lang"]][0],
                                               stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                               universal_newlines=True, creationflags=subprocess.CREATE_NO_WINDOW, shell=False)
                if compilation.communicate()[1]:
                    with sqlite3.connect("dbase.db") as con:
                        cur = con.cursor()
                        cur.execute(f"UPDATE code_task SET status = 'COMPILATION_ERROR' WHERE id = '{db}' ")
                        con.commit()
                    out_result['testing_result']["compilation"] = {'status': 'CE',
                                                                   'checker_answer': 'COMPILATION_ERROR',
                                                                   'time': 0,
                                                                   'memory': 0,
                                                                   'points': 0}
                    out_result['result_all_info']["compilation"] = 'COMPILATION_ERROR'
                    with open(f'instance/protocole/{db}.json', 'w', newline='',
                              encoding="utf-8") as f:
                        json.dump(out_result, f, ensure_ascii=False, indent=4)
                    compilation.kill()
                    return
                else:
                    out_result['result_all_info']["compilation"] = 'OK'
                    out_result['testing_result']["Compilation"] = {'status': 'OK', 'checker_answer': 'OK',
                                                                   'time': 0,
                                                                   'memory': 0,
                                                                   'points': 0}
                compilation.kill()
            else:
                out_result['result_all_info']["compilation"] = 'OK'
                out_result['testing_result']["Compilation"] = {'status': 'OK', 'checker_answer': 'OK',
                                                               'time': 0,
                                                               'memory': 0,
                                                               'points': 0}
            output_ansewer = ''
            input_ansewer = ''
            first_bad_answer = ''
            with sqlite3.connect("dbase.db") as con:
                cur = con.cursor()
                cur.execute(f"UPDATE code_task SET status = 'testing...' WHERE id = '{db}'")
                con.commit()
            for i in range(1, int(test_s) + 1):
                with sqlite3.connect("dbase.db") as con:
                    cur = con.cursor()
                    cur.execute(f"UPDATE code_task SET testing = '{i}' WHERE id = '{db}'")
                    con.commit()
                with open(f'instance/task/{rearg}/tests/input/in-{i}.txt', 'r') as re:
                    input_ansewer = re.read()
                p = subprocess.Popen(compiler[test_info["lang"]][2],
                                     shell=True,
                                     stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                     universal_newlines=True)
                start_time = time.time()
                try:
                    with open(f'instance/task/{rearg}/tests/output/out-{i}.txt', 'r') as re:
                        output_ansewer = re.read()
                    start_time2 = time.time()
                    stdout, stderr = p.communicate(input=input_ansewer, timeout=int(limit) / 1000)
                    print(stderr)
                    res_time = float(f'{(time.time() - start_time2):.3f}')
                    new_file = open(f'instance/answer_user/{db}.txt', 'w+', newline='',
                                    encoding="utf-8")
                    new_file.write(stdout.rstrip('\n'))
                    new_file.close()
                    check_ = subprocess.Popen(
                        [Path(Path().cwd(), "instance", "task", f'{rearg}', 'files', f"{checker_}"),
                         f'instance/task/{rearg}/tests/input/in-{i}.txt',
                         f'instance/task/{rearg}/tests/output/out-{i}.txt', f'instance/answer_user/{db}.txt'],
                        shell=True,
                        stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                        universal_newlines=True)
                    check_result = check_.stderr.readline().strip('\n')
                    if stderr:
                        out_result['testing_result'][f"test_{i}"] = {'status': 'RE',
                                                                     'input-test': input_ansewer,
                                                                     'output-test': output_ansewer,
                                                                     'user-answer': stdout,
                                                                     'checker_answer': check_result,
                                                                     'time': res_time,
                                                                     'memory': 0,
                                                                     'points': 0}
                        out_result['result_all_info']['first_failed_test'] = min(i,
                                                                                 out_result['result_all_info'][
                                                                                     'first_failed_test'])
                        out_result['result_all_info']['failed_test'] += 1
                        out_result['result_all_info']["bad_time"] = max(out_result['result_all_info']["bad_time"],
                                                                        out_result['testing_result'][f"test_{i}"]
                                                                        ['time'])
                        out_result['result_all_info']["bad_memory"] = max(
                            out_result['result_all_info']["bad_memory"],
                            out_result['testing_result'][f"test_{i}"]
                            ['memory'])
                        if not first_bad_answer:
                            first_bad_answer = 'RUN_ERROR'
                    elif 'ok' in check_result:
                        out_result['testing_result'][f"test_{i}"] = {'status': 'OK',
                                                                     'input-test': input_ansewer,
                                                                     'output-test': output_ansewer,
                                                                     'user-answer': stdout,
                                                                     'checker_answer': check_result,
                                                                     'time': res_time,
                                                                     'memory': 0,
                                                                     'points': 1}
                        out_result['result_all_info']['success_test'] += 1
                        out_result['result_all_info']["points"] += 1
                        out_result['result_all_info']["bad_time"] = max(out_result['result_all_info']["bad_time"],
                                                                        out_result['testing_result'][f"test_{i}"]
                                                                        ['time'])
                        out_result['result_all_info']["bad_memory"] = max(
                            out_result['result_all_info']["bad_memory"],
                            out_result['testing_result'][f"test_{i}"]
                            ['memory'])
                    elif 'wrong answer' in check_result:
                        out_result['testing_result'][f"test_{i}"] = {'status': 'WA',
                                                                     'input-test': input_ansewer,
                                                                     'output-test': output_ansewer,
                                                                     'user-answer': stdout,
                                                                     'checker_answer': check_result,
                                                                     'time': res_time,
                                                                     'memory': 0,
                                                                     'points': 0}
                        out_result['result_all_info']['first_failed_test'] = min(i,
                                                                                 out_result['result_all_info'][
                                                                                     'first_failed_test'])
                        out_result['result_all_info']['failed_test'] += 1
                        out_result['result_all_info']["bad_time"] = max(out_result['result_all_info']["bad_time"],
                                                                        out_result['testing_result'][f"test_{i}"]
                                                                        ['time'])
                        out_result['result_all_info']["bad_memory"] = max(
                            out_result['result_all_info']["bad_memory"],
                            out_result['testing_result'][f"test_{i}"]
                            ['memory'])
                        if not first_bad_answer:
                            first_bad_answer = 'WRONG_ANSWER'
                    elif 'wrong output' in check_result:
                        out_result['testing_result'][f"test_{i}"] = {'status': 'PE',
                                                                     'input-test': input_ansewer,
                                                                     'output-test': output_ansewer,
                                                                     'user-answer': stdout,
                                                                     'checker_answer': check_result,
                                                                     'time': res_time,
                                                                     'memory': 0,
                                                                     'points': 0}
                        out_result['result_all_info']['first_failed_test'] = min(i,
                                                                                 out_result['result_all_info'][
                                                                                     'first_failed_test'])
                        out_result['result_all_info']['failed_test'] += 1
                        out_result['result_all_info']["bad_time"] = max(out_result['result_all_info']["bad_time"],
                                                                        out_result['testing_result'][f"test_{i}"]
                                                                        ['time'])
                        out_result['result_all_info']["bad_memory"] = max(
                            out_result['result_all_info']["bad_memory"],
                            out_result['testing_result'][f"test_{i}"]
                            ['memory'])
                        if not first_bad_answer:
                            first_bad_answer = 'PRESENTATION_ERROR'
                    check_.kill()
                    p.kill()
                except subprocess.TimeoutExpired:
                    out_result['testing_result'][f"test_{i}"] = {'status': 'TL',
                                                                 'input-test': input_ansewer,
                                                                 'output-test': output_ansewer,
                                                                 'user-answer': 'NOT ANSWER',
                                                                 'checker_answer': 'TIME_LIMIT',
                                                                 'time': float(f'{(time.time() - start_time):.3f}'),
                                                                 'memory': 0,
                                                                 'points': 0}
                    out_result['result_all_info']['first_failed_test'] = min(i,
                                                                             out_result['result_all_info'][
                                                                                 'first_failed_test'])
                    out_result['result_all_info']['failed_test'] += 1
                    out_result['result_all_info']["bad_time"] = max(out_result['result_all_info']["bad_time"],
                                                                    out_result['testing_result'][f"test_{i}"]
                                                                    ['time'])
                    out_result['result_all_info']["bad_memory"] = max(
                        out_result['result_all_info']["bad_memory"],
                        out_result['testing_result'][f"test_{i}"]
                        ['memory'])
                    if not first_bad_answer:
                        first_bad_answer = 'TIME_LIMIT'
                    p.kill()
                with open(f'instance/protocole/{db}.json', 'w', newline='',
                          encoding="utf-8") as f:
                    json.dump(out_result, f, ensure_ascii=False, indent=4)
            with sqlite3.connect("dbase.db") as con:
                cur = con.cursor()
                status = 'OK'
                failed = -1
                if out_result['result_all_info']['first_failed_test'] != int(test_s) + 1:
                    failed = out_result['result_all_info']['first_failed_test']
                if out_result['result_all_info']['success_test'] != out_result['result_all_info']['all_test']:
                    status = first_bad_answer
                cur.execute(f"UPDATE code_task SET protocole = '{db}', "
                            f"status = '{status}', "
                            f"fail= '{failed}', "
                            f"bad_time = '{out_result['result_all_info']['bad_time']}', "
                            f"bad_memory = '{out_result['result_all_info']['bad_memory']}', "
                            f"points = '{out_result['result_all_info']['points']}'  WHERE id = '{db}'")
                con.commit()
        except ErrorTesting:
            with sqlite3.connect("dbase.db") as con:
                cur = con.cursor()
                cur.execute(f"UPDATE code_task SET status = 'bruh' WHERE id = '{db}'")
                con.commit()

    def compiler(self, db):
        return {
            'python3': [
                [f'NO COMPILER'],
                'py',
                [f'python', f'{Path(Path().cwd(), "instance", "post_files", f"{db}.py")}'],
                'python 3.10'],
            'pypy3': [
                [f'NO COMPILER'],
                'py',
                [f'pypy', f'{Path(Path().cwd(), "instance", "post_files", f"{db}.py")}'],
                'pypy 3.9'],
            'gcc': ['gcc.exe', 'cs'],
            'gnu20': [
                ['g++.exe', '-static', '-DONLINE_JUDGE', '-lm', '-s', '-x', 'c++', '-Wl,--stack=268435456', '-O2'
                    , '-std=c++20', '-D__USE_MINGW_ANSI_STDIO=0', '-o',
                 f'{Path(Path().cwd(), "instance", "post_files", f"{db}.exe")}',
                 f'{Path(Path().cwd(), "instance", "post_files", f"{db}.cpp")}'],
                'cpp',
                [f'{Path(Path().cwd(), "instance", "post_files", f"{db}.exe")}'],
                'GNU C++ 20'], 'java17': ['Java 17', 'jar'],
            'js9': ['JavaScript 9', 'js'],
            'freepascal': ['Free Pascal 3.0.4', 'txt']}
