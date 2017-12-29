from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import sqlite3

#roll numbers formats for various departments, change according to requirement
depts = [101114000,102114000,103114000,106114000,107114000,108114000,110114000,111114000,112114000,114114000]
first_no = 1
last_no = 110

for i in depts:
    for roll_no in range(i+first_no, i+last_no):
        #open page through firefox browser
        driver = webdriver.Firefox()
        driver.get("http://www.nitt.edu/prm/nitreg/ShowRes.aspx")

        #find text box and insert value, click on submit button
        tbox = driver.find_element_by_id('TextBox1')
        tbox.clear()
        tbox.send_keys(roll_no)

        submit_button = driver.find_element_by_id('Button1')
        submit_button.click()

        # wait till dropdown loads and select
        try:
            element_present = EC.presence_of_element_located((By.ID, 'Dt1'))
            WebDriverWait(driver, 10).until(element_present)
        except:
            print(roll_no, "did not load")
            driver.quit()
            continue

        dropdown = Select(driver.find_element_by_tag_name('select'))
        dropdown.select_by_visible_text("NOV-2017 (REGULAR)")

        #wait till table loads and select
        try:
            element_present = EC.presence_of_element_located((By.ID, 'DataGrid1'))
            WebDriverWait(driver, 10).until(element_present)
        except:
            print(roll_no, "did not load")
            driver.quit()
            continue

        #get rows, remove heading
        rows = driver.find_element_by_id('DataGrid1').find_elements_by_tag_name('tr')
        rows.pop(0)

        sql_rows = []

        #parse rows and store each row as a list
        for row in rows:
            elems = row.find_elements_by_tag_name('font')
            sql_data = []
            for elem in elems:
                sql_data.append(elem.text)
            sql_data.insert(1,roll_no)
            sql_data.pop(0)
            sql_data[3] = int(sql_data[3])
            sql_rows.append(sql_data)

        #insert into db
        conn = sqlite3.connect("nitt_results.db")

        command = """
        CREATE TABLE IF NOT EXISTS results (
        roll_no INTEGER,
        subject_code VARCHAR(5),
        subject_name VARCHAR(100),
        credits INTEGER,
        grade CHAR(1),
        attendance CHAR(1)); """

        cur = conn.cursor()

        cur.execute(command)

        for row in sql_rows:
            command = """
            INSERT INTO results VALUES (
            "{roll_no}","{subject_code}","{subject_name}","{credits}","{grade}","{attendance}");
           """
            sql_command = command.format(roll_no = row[0], subject_code = row[1], subject_name=row[2], credits = row[3], grade = row[4], attendance = row[5])
            cur.execute(sql_command);

        conn.commit()
        conn.close()


        driver.quit()
