import io
import sys
import random
import re
import riegeli
import contest_problem_pb2
import pandas as pd


def remove_illegal_chars(text):
    """Clean illegal Excel control characters."""
    if not isinstance(text, str):
        return text
    # 去掉 Excel 无法识别的控制符
    return re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F]', '', text)


def _all_problems(filenames):
    """Iterates through all ContestProblems in filenames and logs per-file progress."""
    for idx, filename in enumerate(filenames, start=1):
        print(f"[INFO] Starting file {idx}/{len(filenames)}: {filename}", flush=True)
        num_problems = 0
        reader = riegeli.RecordReader(io.FileIO(filename, mode='rb'))
        for problem in reader.read_messages(contest_problem_pb2.ContestProblem):
            yield problem
            num_problems += 1
            if num_problems % 1000 == 0:
                print(f"    Processed {num_problems} problems in current shard...", flush=True)
        print(f"[INFO] Finished file {idx}/{len(filenames)} ({num_problems} problems).", flush=True)


def _filter_cross_language_equivalent(filenames, output_xlsx, seed=42):
    """Filter problems having at least one non-empty pass solution in C++, Java, and Python3."""
    random.seed(seed)
    records = []
    count_total = 0
    count_selected = 0

    for problem in _all_problems(filenames):
        count_total += 1

        # Collect non-empty pass solutions by language
        lang_solutions = {"CPP": [], "JAVA": [], "PYTHON3": []}
        for sol in problem.solutions:
            lang_name = contest_problem_pb2.ContestProblem.Solution.Language.Name(sol.language)
            # ✅ 过滤空字符串或空白代码
            if lang_name in lang_solutions and sol.solution.strip():
                lang_solutions[lang_name].append(sol.solution)

        # Keep only problems that have all three languages with non-empty code
        if all(len(v) > 0 for v in lang_solutions.values()):
            count_selected += 1
            cpp_code = random.choice(lang_solutions["CPP"])
            java_code = random.choice(lang_solutions["JAVA"])
            py_code = random.choice(lang_solutions["PYTHON3"])

            source_name = contest_problem_pb2.ContestProblem.Source.Name(problem.source)
            description = problem.description if problem.HasField("description") else ""

            # ✅ 清理非法字符
            record = {
                "Source": remove_illegal_chars(source_name),
                "ProblemName": remove_illegal_chars(problem.name),
                "Description": remove_illegal_chars(description),
                "CPP_Solution": remove_illegal_chars(cpp_code),
                "JAVA_Solution": remove_illegal_chars(java_code),
                "PYTHON3_Solution": remove_illegal_chars(py_code),
            }

            records.append(record)
            print(f"[SELECTED] {problem.name} ({source_name}) ✅", flush=True)
        else:
            missing_langs = [k for k, v in lang_solutions.items() if len(v) == 0]
            print(f"[SKIP] {problem.name} ({contest_problem_pb2.ContestProblem.Source.Name(problem.source)}) missing {missing_langs}", flush=True)

    # Convert to DataFrame and clean again
    df = pd.DataFrame(records)
    df = df.applymap(remove_illegal_chars)
    df.to_excel(output_xlsx, index=False)

    print(f"\n[SUMMARY] Processed {count_total} problems, selected {count_selected}.")
    print(f"[SUMMARY] Saved results to: {output_xlsx}")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python print_names_and_sources.py /path/to/train/files* output.xlsx")
        sys.exit(1)

    filenames = sys.argv[1:-1]
    output_xlsx = sys.argv[-1]
    _filter_cross_language_equivalent(filenames, output_xlsx)




# bazel run -c opt :print_names_and_sources -- \
# /tmp/dm-code_contests/code_contests_train.riegeli-* \
# /home/hsun26/idealProject/semanticEquivalent/code_contests/cross_lang_equiv_clean.xlsx
