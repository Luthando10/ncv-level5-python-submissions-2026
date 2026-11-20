"""
Community Water Consumption and Billing Management System
File: water_billing.py
Dataset: water_readings.txt - 220 household records
"""

# ============================================================
# Q1 - READ FILE + HANDLE MISSING FILE
# ============================================================
def read_file(filename):
    """Read all lines from file. Return list of lines or None if missing."""
    try:
        file = open(filename, "r")
        lines = file.readlines()
        file.close()
        return lines
    except FileNotFoundError:
        print("ERROR: File '" + filename + "' not found.")
        print("Please make sure water_readings.txt is in the same folder as water_billing.py")
        return None

# ============================================================
# Q5 - CALCULATE BILL - PROGRESSIVE TARIFF
# ============================================================
def calculate_bill(consumption):
    """
    Progressive tariff:
    First 6 kL                : Free
    Next 14 kL (6 to 20)      : R8.50 per kL
    Above 20 kL              : R12.00 per kL
    Example: 25 kL = (14 x 8.50) + (5 x 12.00) = R179.00
    """
    bill = 0.0
    if consumption <= 6:
        bill = 0.0
    elif consumption <= 20:
        bill = (consumption - 6) * 8.50
    else:
        bill = (14 * 8.50) + ((consumption - 20) * 12.00)
    return bill

# ============================================================
# Q6 - CLASSIFY CONSUMPTION
# ============================================================
def classify_consumption(consumption):
    """LOW = 0-20, MODERATE = 21-50, HIGH = above 50"""
    if consumption <= 20:
        return "LOW"
    elif consumption <= 50:
        return "MODERATE"
    else:
        return "HIGH"

# ============================================================
# Q7 - MANUAL RANKING - TOP 5 (NO sorted/max/min/sum)
# ============================================================
def find_top_five(households):
    """
    Manually rank top 5 using loops only.
    households: meter -> [name, prev, curr, area, consumption, bill, category]
    """
    top_five = []

    for meter in households:
        record = households[meter]
        name = record[0]
        area = record[3]
        consumption = record[4]
        bill = record[5]
        category = record[6]
        current = [meter, name, area, consumption, bill, category]

        if len(top_five) < 5:
            top_five.append(current)
        else:
            # Find smallest in top five - manual loop
            smallest_index = 0
            smallest_value = top_five[0][3]
            i = 1
            while i < len(top_five):
                if top_five[i][3] < smallest_value:
                    smallest_value = top_five[i][3]
                    smallest_index = i
                i = i + 1
            if consumption > smallest_value:
                top_five[smallest_index] = current

    # Bubble Sort descending - manual
    n = len(top_five)
    pass_num = 0
    while pass_num < n - 1:
        j = 0
        while j < n - 1 - pass_num:
            if top_five[j][3] < top_five[j + 1][3]:
                temp = top_five[j]
                top_five[j] = top_five[j + 1]
                top_five[j + 1] = temp
            j = j + 1
        pass_num = pass_num + 1

    return top_five

# ============================================================
# MAIN PROGRAM
# ============================================================
def main():
    input_file = "water_readings.txt"
    report_file = "billing_report.txt"
    error_file = "errors.log"

    # ---- Q1: Read file ----
    lines = read_file(input_file)
    if lines is None:
        return

    # ---- Q2 + Q3: Split, clean, validate, store in dictionary ----
    households = {}  # meter -> [name, prev, curr, area, consumption, bill, category]
    errors = []
    total_lines = 0
    accepted = 0
    rejected = 0

    for raw_line in lines:
        line = raw_line.strip()
        if line == "":
            continue
        total_lines = total_lines + 1

        parts = line.split(",")

        # Q3a: Must have exactly 5 fields
        if len(parts) != 5:
            errors.append("Line: '" + line + "' | REASON: Missing fields - expected 5 fields, found " + str(len(parts)))
            rejected = rejected + 1
            continue

        meter = parts[0].strip()
        name = parts[1].strip()
        prev_str = parts[2].strip()
        curr_str = parts[3].strip()
        area = parts[4].strip()

        # Q3b: Empty fields
        if meter == "" or name == "" or prev_str == "" or curr_str == "" or area == "":
            errors.append("Line: '" + line + "' | REASON: Missing field - one or more fields are empty")
            rejected = rejected + 1
            continue

        # Q3c: Duplicate meter
        if meter in households:
            errors.append("Line: '" + line + "' | REASON: Duplicate meter number '" + meter + "' - already exists")
            rejected = rejected + 1
            continue

        # Q3d: Non-numeric
        try:
            previous = int(prev_str)
            current = int(curr_str)
        except ValueError:
            errors.append("Line: '" + line + "' | REASON: Non-numeric reading - Previous='" + prev_str + "' Current='" + curr_str + "' must be integers")
            rejected = rejected + 1
            continue

        # Q3e: Negative
        if previous < 0 or current < 0:
            errors.append("Line: '" + line + "' | REASON: Negative reading - Previous=" + str(previous) + " Current=" + str(current) + " readings cannot be negative")
            rejected = rejected + 1
            continue

        # Q3f: Current below previous
        if current < previous:
            errors.append("Line: '" + line + "' | REASON: Current reading (" + str(current) + ") is below previous reading (" + str(previous) + ")")
            rejected = rejected + 1
            continue

        # ---- Q4: Consumption ----
        consumption = current - previous

        # ---- Q5: Bill ----
        bill = calculate_bill(consumption)

        # ---- Q6: Classify ----
        category = classify_consumption(consumption)

        # ---- Q2: Store in dictionary ----
        households[meter] = [name, previous, current, area, consumption, bill, category]
        accepted = accepted + 1

    # ---- Q7: Top Five ----
    top_five = find_top_five(households)

    # ---- Summary totals using LOOPS (not sum()) ----
    total_consumption = 0
    total_billed = 0.0
    count_low = 0
    count_moderate = 0
    count_high = 0

    for meter in households:
        rec = households[meter]
        total_consumption = total_consumption + rec[4]
        total_billed = total_billed + rec[5]
        if rec[6] == "LOW":
            count_low = count_low + 1
        elif rec[6] == "MODERATE":
            count_moderate = count_moderate + 1
        else:
            count_high = count_high + 1

    if accepted > 0:
        avg_consumption = total_consumption / accepted
    else:
        avg_consumption = 0

    # ---- Q8: Write billing_report.txt ----
    report = open(report_file, "w")
    report.write("=" * 70 + "\n")
    report.write("COMMUNITY WATER CONSUMPTION AND BILLING REPORT\n")
    report.write("=" * 70 + "\n")
    report.write("Billing Period: Monthly\n")
    report.write("Tariff: First 6 kL Free | Next 14 kL @ R8.50/kL | Above 20 kL @ R12.00/kL\n")
    report.write("-" * 70 + "\n\n")

    report.write("HOUSEHOLD BILLING DETAILS\n")
    report.write("-" * 70 + "\n")
    report.write(f"{'Meter':<8} {'Name':<22} {'Area':<16} {'Cons(kL)':>8} {'Category':<10} {'Bill(R)':>9}\n")
    report.write("-" * 70 + "\n")

    # Sort meter list manually - Bubble Sort (no sorted())
    meter_list = []
    for m in households:
        meter_list.append(m)
    a = 0
    while a < len(meter_list) - 1:
        b = 0
        while b < len(meter_list) - 1 - a:
            if meter_list[b] > meter_list[b + 1]:
                t = meter_list[b]
                meter_list[b] = meter_list[b + 1]
                meter_list[b + 1] = t
            b = b + 1
        a = a + 1

    for meter in meter_list:
        rec = households[meter]
        report.write(f"{meter:<8} {rec[0]:<22} {rec[3]:<16} {rec[4]:>8} {rec[6]:<10} {rec[5]:>9.2f}\n")

    report.write("\n" + "-" * 70 + "\n")
    report.write("TOP 5 HIGHEST CONSUMING HOUSEHOLDS\n")
    report.write("-" * 70 + "\n")
    report.write(f"{'Rank':<6} {'Meter':<8} {'Name':<22} {'Area':<16} {'Cons(kL)':>8} {'Bill(R)':>9}\n")
    rank = 1
    for entry in top_five:
        report.write(f"{rank:<6} {entry[0]:<8} {entry[1]:<22} {entry[2]:<16} {entry[3]:>8} {entry[4]:>9.2f}\n")
        rank = rank + 1

    report.write("\n" + "-" * 70 + "\n")
    report.write("SUMMARY\n")
    report.write("-" * 70 + "\n")
    report.write("Total records processed: " + str(total_lines) + "\n")
    report.write("Accepted (valid) records: " + str(accepted) + "\n")
    report.write("Rejected (invalid) records: " + str(rejected) + "\n")
    report.write("Total consumption: " + str(total_consumption) + " kL\n")
    report.write("Average consumption per household: " + f"{avg_consumption:.2f}" + " kL\n")
    report.write("Total amount billed: R" + f"{total_billed:.2f}" + "\n")
    report.write("LOW (0-20 kL): " + str(count_low) + " households\n")
    report.write("MODERATE (21-50 kL): " + str(count_moderate) + " households\n")
    report.write("HIGH (above 50 kL): " + str(count_high) + " households\n")
    report.write("=" * 70 + "\n")
    report.close()

    # ---- Q8: Write errors.log ----
    err = open(error_file, "w")
    err.write("=" * 70 + "\n")
    err.write("ERROR LOG - REJECTED RECORDS\n")
    err.write("=" * 70 + "\n")
    if len(errors) == 0:
        err.write("No errors found. All records accepted.\n")
    else:
        i = 0
        while i < len(errors):
            err.write(str(i + 1) + ". " + errors[i] + "\n")
            i = i + 1
    err.write("-" * 70 + "\n")
    err.write("Total rejected: " + str(rejected) + "\n")
    err.close()

    # ---- Q8: Display totals ----
    print("=" * 70)
    print("WATER BILLING PROCESSING COMPLETE")
    print("=" * 70)
    print("Total records processed:", total_lines)
    print("Accepted (valid):", accepted)
    print("Rejected (invalid):", rejected)
    print("Total consumption:", total_consumption, "kL")
    print("Total billed: R" + f"{total_billed:.2f}")
    print("LOW:", count_low, "| MODERATE:", count_moderate, "| HIGH:", count_high)
    print()
    print("Top 5 Consumers:")
    r = 1
    for entry in top_five:
        print(str(r) + ". " + entry[0] + " - " + entry[1] + " (" + entry[2] + ") - " + str(entry[3]) + " kL - R" + f"{entry[4]:.2f}")
        r = r + 1
    print()
    print("Files created: billing_report.txt and errors.log")

if __name__ == "__main__":
    main()