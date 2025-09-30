import os
import string

import os
import string

def generate_egtask_xml(
    fds_file="bart_out/HOSP.fds",
    csv_path="/home/chandlernick/BHT/Research/error-paper/data/hospital/clean.csv",
    output_xml="bart_task.xml",
    db_host="127.0.0.1",
    db_port=5432,
    db_name="postgres",
    db_user="postgres",
    db_password="yourpassword",
    schema="public",
    output_dir="/home/chandlernick/BHT/Research/error-paper/benchmarks/ic-baseline/output/"
):
    """
    Generate a full EGTask XML for BART from a .fds file using the
    $varN notation for variable instances and adding <vioGenQuery> entries.
    """
    # Read FDs
    fds = []
    with open(fds_file) as f:
        for line in f:
            line = line.strip()
            if "->" in line:
                lhs, rhs = line.split("->")
                lhs_attrs = [a.strip() for a in lhs.split(",")]
                rhs_attr = rhs.strip()
                fds.append((lhs_attrs, rhs_attr))

    # Build dependencies block
    dep_lines = ["<![CDATA[", "DCs:"]
    vio_gen_queries = []
    for idx, (lhs, rhs) in enumerate(fds, start=1):
        # Variable names
        var_map = {}
        letters = string.ascii_lowercase
        for i, attr in enumerate(lhs + [rhs]):
            var_map[attr] = (f"${letters[i]}1", f"${letters[i]}2")

        # LHS tuples
        lhs_pairs = ", ".join(f"{attr}: {var_map[attr][0]}" for attr in lhs)
        lhs_pairs_2 = ", ".join(f"{attr}: {var_map[attr][1]}" for attr in lhs)
        rhs_pair_1 = var_map[rhs][0]
        rhs_pair_2 = var_map[rhs][1]

        # Build dependency
        lhs_equalities = ", ".join(f"{var_map[attr][0]} == {var_map[attr][1]}" for attr in lhs)
        dep_lines.append(
            f"e{idx}: person({lhs_pairs}, {rhs}: {rhs_pair_1}), "
            f"person({lhs_pairs_2}, {rhs}: {rhs_pair_2}), "
            f"{lhs_equalities}, {rhs_pair_1} != {rhs_pair_2} -> #fail."
        )

        # Add vioGenQuery for configuration
        vio_gen_queries.append(
            f"""    <vioGenQuery id="e{idx}">
        <comparison>({rhs_pair_1} != {rhs_pair_2})</comparison>
        <percentage>1.0</percentage>
    </vioGenQuery>"""
        )

    dep_lines.append("]]>")
    dependencies_block = "\n".join(dep_lines)
    vio_gen_block = "\n".join(vio_gen_queries)

    # Build the full XML
    xml_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<task>
    <target> 
        <type>DBMS</type>
        <access-configuration>
            <driver>org.postgresql.Driver</driver>
            <uri>jdbc:postgresql://{db_host}:{db_port}/{db_name}</uri>
            <schema>{schema}</schema>
            <login>{db_user}</login>
            <password>{db_password}</password>
        </access-configuration>
        <import>
            <input type="csv" separator="," table="hosp">{csv_path}</input>
        </import>
    </target>

    <dependencies>
{dependencies_block}
    </dependencies>

    <configuration>
        <printLog>true</printLog>
        <recreateDBOnStart>false</recreateDBOnStart>
        <applyCellChanges>true</applyCellChanges>
        <cloneTargetSchema>true</cloneTargetSchema>
        <cloneSuffix>_dirty</cloneSuffix>
        <exportDirtyDB>true</exportDirtyDB>
        <exportDirtyDBPath>{output_dir}</exportDirtyDBPath>
        <exportDirtyDBType>CSV</exportDirtyDBType>
        <exportCellChanges>true</exportCellChanges>
        <exportCellChangesPath>{os.path.join(output_dir,"changes.csv")}</exportCellChangesPath>
        <estimateRepairability>true</estimateRepairability>
        <useDeltaDBForChanges>true</useDeltaDBForChanges>
        <avoidInteractions>true</avoidInteractions>
        <checkChanges>true</checkChanges>
        <generateAllChanges>false</generateAllChanges>

        <!-- NEW BLOCKS TO ACTUALLY MAKE DATA DIRTY -->
        <errorPercentages>
            <defaultPercentage>0.25</defaultPercentage>
{vio_gen_block}
        </errorPercentages>

        <dirtyStrategies>
            <defaultStrategy>
                <strategy chars="*" charsToAdd="3">TypoAddString</strategy>
            </defaultStrategy>
        </dirtyStrategies>

        <vioGenQueriesConfiguration>
            <probabilityFactorForStandardQueries>0.5</probabilityFactorForStandardQueries>
            <offsetFactorForStandardQueries>0.05</offsetFactorForStandardQueries>
            <probabilityFactorForSymmetricQueries>0.5</probabilityFactorForSymmetricQueries>
            <offsetFactorForSymmetricQueries>0.05</offsetFactorForSymmetricQueries>
            <probabilityFactorForInequalityQueries>0.25</probabilityFactorForInequalityQueries>
            <offsetFactorForInequalityQueries>0.05</offsetFactorForInequalityQueries>
            <windowSizeFactorForInequalityQueries>1.5</windowSizeFactorForInequalityQueries>
        </vioGenQueriesConfiguration>

    </configuration>
</task>
"""
    with open(output_xml, "w") as f:
        f.write(xml_content)
    print(f"EGTask XML generated at {output_xml}")


if __name__ == "__main__":
    generate_egtask_xml()