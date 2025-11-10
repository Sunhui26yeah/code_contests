import io
import sys
import random
import re
import riegeli
import contest_problem_pb2
import pandas as pd


# ========== Helper Functions ==========

def remove_illegal_chars(text):
    """Clean illegal Excel control characters and normalize newlines."""
    if not isinstance(text, str):
        return text
    text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F]', '', text)  # Remove control chars
    text = text.replace('\r\n', '\n').replace('\r', '\n')  # Normalize line breaks
    return text


def sanitize_code(code):
    """Clean and safely store multi-line code."""
    if not isinstance(code, str):
        return code
    code = remove_illegal_chars(code)
    code = code.strip()
    # 防止Excel中换行导致显示错位（将 \n 保留但显式可识别）
    return code.replace('\n', '\n')  


def _all_problems(filenames):
    """Safely iterate through Riegeli ContestProblem records."""
    for idx, filename in enumerate(filenames, start=1):
        print(f"[INFO] Starting file {idx}/{len(filenames)}: {filename}", flush=True)
        num_problems = 0
        with riegeli.RecordReader(io.FileIO(filename, mode='rb')) as reader:
            for problem in reader.read_messages(contest_problem_pb2.ContestProblem):
                yield filename, problem
                num_problems += 1
                if num_problems % 1000 == 0:
                    print(f"    Processed {num_problems} problems in current shard...", flush=True)
        print(f"[INFO] Finished file {idx}/{len(filenames)} ({num_problems} problems).", flush=True)


def _filter_fully_valid_equiv(filenames, output_xlsx, seed=41):
    """Extract problems satisfying all three semantic-equivalence conditions."""
    random.seed(seed)
    records = []
    count_total = 0
    count_selected = 0

    for filename, problem in _all_problems(filenames):
        count_total += 1
        lang_groups = {
            "CPP": {"pass": [], "fail": []},
            "JAVA": {"pass": [], "fail": []},
            "PYTHON3": {"pass": [], "fail": []},
        }

        # Collect passed solutions
        for sol in problem.solutions:
            lang_name = contest_problem_pb2.ContestProblem.Solution.Language.Name(sol.language)
            if lang_name in lang_groups and sol.solution.strip():
                lang_groups[lang_name]["pass"].append(sol.solution)

        # Collect failed solutions
        for sol in problem.incorrect_solutions:
            lang_name = contest_problem_pb2.ContestProblem.Solution.Language.Name(sol.language)
            if lang_name in lang_groups and sol.solution.strip():
                lang_groups[lang_name]["fail"].append(sol.solution)

        # Count per-language
        cpp_pass, cpp_fail = len(lang_groups["CPP"]["pass"]), len(lang_groups["CPP"]["fail"])
        java_pass, java_fail = len(lang_groups["JAVA"]["pass"]), len(lang_groups["JAVA"]["fail"])
        py_pass, py_fail = len(lang_groups["PYTHON3"]["pass"]), len(lang_groups["PYTHON3"]["fail"])

        # Conditions
        all_langs_have_pass = all(len(v["pass"]) >= 1 for v in lang_groups.values())
        each_has_two_pass = all(len(v["pass"]) >= 2 for v in lang_groups.values())
        each_has_fail = all(len(v["fail"]) >= 1 for v in lang_groups.values())

        # Seed offset per problem to ensure deterministic random choice
        random.seed(seed + count_total)

        if all_langs_have_pass and each_has_two_pass and each_has_fail:
            count_selected += 1

            cpp_passes = random.sample(lang_groups["CPP"]["pass"], 2)
            java_passes = random.sample(lang_groups["JAVA"]["pass"], 2)
            py_passes = random.sample(lang_groups["PYTHON3"]["pass"], 2)

            cpp_fail_sample = random.choice(lang_groups["CPP"]["fail"])
            java_fail_sample = random.choice(lang_groups["JAVA"]["fail"])
            py_fail_sample = random.choice(lang_groups["PYTHON3"]["fail"])

            source_name = contest_problem_pb2.ContestProblem.Source.Name(problem.source)
            description = problem.description if problem.HasField("description") else ""
            diff_label = contest_problem_pb2.ContestProblem.Difficulty.Name(problem.difficulty)

            record = {
                "Source": remove_illegal_chars(source_name),
                "File": remove_illegal_chars(filename),
                "ProblemName": remove_illegal_chars(problem.name),
                "Description": remove_illegal_chars(description),
                "Difficulty": remove_illegal_chars(diff_label),

                # Pass/fail counts
                "CPP_PassCount": cpp_pass, "CPP_FailCount": cpp_fail,
                "JAVA_PassCount": java_pass, "JAVA_FailCount": java_fail,
                "PYTHON3_PassCount": py_pass, "PYTHON3_FailCount": py_fail,

                # Sampled code
                "CPP_Pass1": sanitize_code(cpp_passes[0]),
                "CPP_Pass2": sanitize_code(cpp_passes[1]),
                "CPP_Fail": sanitize_code(cpp_fail_sample),
                "JAVA_Pass1": sanitize_code(java_passes[0]),
                "JAVA_Pass2": sanitize_code(java_passes[1]),
                "JAVA_Fail": sanitize_code(java_fail_sample),
                "PYTHON3_Pass1": sanitize_code(py_passes[0]),
                "PYTHON3_Pass2": sanitize_code(py_passes[1]),
                "PYTHON3_Fail": sanitize_code(py_fail_sample),
            }

            records.append(record)
            print(
                f"[SELECTED ✅] {problem.name} | Difficulty={diff_label} | "
                f"CPP(pass={cpp_pass},fail={cpp_fail}) JAVA(pass={java_pass},fail={java_fail}) "
                f"PYTHON3(pass={py_pass},fail={py_fail}) | From {filename}",
                flush=True
            )
        else:
            print(
                f"[SKIP ❌] {problem.name} | "
                f"CPP(pass={cpp_pass},fail={cpp_fail}) JAVA(pass={java_pass},fail={java_fail}) "
                f"PYTHON3(pass={py_pass},fail={py_fail}) | Missing condition(s)",
                flush=True
            )

    # Save
    df = pd.DataFrame(records)
    df = df.applymap(remove_illegal_chars)

    print(f"\n[SUMMARY] Processed {count_total} problems, selected {count_selected}.")
    print(f"[SUMMARY] Saving results to: {output_xlsx}")

    # Use openpyxl engine to avoid formatting bugs
    df.to_excel(output_xlsx, index=False, engine="openpyxl")
    print(f"[DONE] Excel export complete. File: {output_xlsx}")


# ========== Main Entry ==========
if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python filter_equiv_fixed.py /path/to/train/files* output.xlsx")
        sys.exit(1)

    filenames = sys.argv[1:-1]
    output_xlsx = sys.argv[-1]
    _filter_fully_valid_equiv(filenames, output_xlsx)




# bazel run -c opt :print_names_and_sources -- \
# /tmp/dm-code_contests/code_contests_train.riegeli-* \
# /home/hsun26/idealProject/semanticEquivalent/code_contests/cross_lang_equiv_clean.xlsx
# bazel run -c opt :print_names_and_sources -- \
# /tmp/dm-code_contests/code_contests_train.riegeli-* \
# /home/hsun26/idealProject/semanticEquivalent/code_contests/full_equiv_output.xlsx
