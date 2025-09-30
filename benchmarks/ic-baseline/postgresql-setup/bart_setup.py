import desbordante
from pathlib import Path

def save_fds(fds, output_file="HOSP.fds"):
    with open(output_file, "w") as f:
        for fd in fds:
            lhs, rhs = fd.to_name_tuple()
            lhs_str = ",".join(lhs)
            f.write(f"{lhs_str} -> {rhs}\n")

def generate_bart_rules_and_queries(fds, table="hospital", out_dir="bart_out"):
    out = Path(out_dir)
    out.mkdir(exist_ok=True)

    rules_file = out / "rules.txt"
    queries_file = out / "violations.xml"

    with open(rules_file, "w") as rf, open(queries_file, "w") as qf:
        qf.write("<vioGenQueries>\n")
        for i, fd in enumerate(fds, 1):
            lhs, rhs = fd.to_name_tuple()
            lhs_lower = [a.lower() for a in lhs]
            rhs_lower = rhs.lower()

            # Prolog-like rule
            lhs_str1 = ", ".join([f"{a.lower()}: ${a.lower()}1" for a in lhs_lower] + [f"{rhs_lower}: ${rhs_lower}1"])
            lhs_str2 = ", ".join([f"{a.lower()}: ${a.lower()}2" for a in lhs_lower] + [f"{rhs_lower}: ${rhs_lower}2"])
            conds = ", ".join([f"${a.lower()}1 == ${a.lower()}2" for a in lhs_lower] + [f"${rhs_lower}1 != ${rhs_lower}2"])
            rule = f"// FD: {','.join(lhs)} -> {rhs}\n" \
                   f"e{i}: {table}({lhs_str1}), {table}({lhs_str2}), {conds} -> #fail.\n\n"
            rf.write(rule)

            # XML query
            qf.write(f"""  <vioGenQuery id="e{i}">
    <comparison>({rhs_lower}1 != {rhs_lower}2)</comparison>
    <percentage>1.0</percentage>
  </vioGenQuery>\n""")

        qf.write("</vioGenQueries>\n")

    print(f"Wrote BART rules to {rules_file}")
    print(f"Wrote vioGenQueries to {queries_file}")

def generate_bart_conf(dbname, user, password, table, fds_file="HOSP.fds", host="localhost", port=5432, out_file="bart_out/config.conf"):
    conf = f"""# Database connection
dbms=postgres
db_driver=org.postgresql.Driver
db_url=jdbc:postgresql://{host}:{port}/{dbname}
db_user={user}
db_password={password}

# Dataset
table={table}
separator=,

# FDs
fds={fds_file}
"""
    Path(out_file).write_text(conf)
    print(f"Wrote BART config to {out_file}")

if __name__ == "__main__":
    algo = desbordante.fd.algorithms.Default()
    algo.load_data(table=("../../../data/hospital/clean.csv", ",", True))
    algo.execute()
    fds = algo.get_fds()

    # Step 1: Save .fds
    save_fds(fds, "bart_out/HOSP.fds")

    # Step 2: Generate rules + queries
    generate_bart_rules_and_queries(fds, table="hospital", out_dir="bart_out")

    # Step 3: Generate config file
    generate_bart_conf(
    dbname="postgres",
    user="postgres",
    password="yourpassword",
    table="hosp",
    fds_file="bart_out/HOSP.fds",
    host="127.0.0.1",            # since we're port-forwarding
    port=5432,                    # local forwarded port
    out_file="bart_out/config.conf"
    )
