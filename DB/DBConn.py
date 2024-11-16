#-*- coding: utf-8 -*-
import pymssql

# DB 서버 주소
#server = '175.197.7.159'
server = '27.35.75.254'
# 데이터 베이스 이름
database = 'changejob'
# 접속 유저명
username = 'py'
# 접속 유저 패스워드
password = '1234'

# MSSQL 접속
#컬럼명으로 조회
#cnxn = pymssql.connect(server, username, password, database, charset='utf8', as_dict=True)
#인덱스로 조회
cnxn = pymssql.connect(server, username, password, database, charset='utf8')
cursor = cnxn.cursor()

# SQL문 실행
#cursor.execute('SELECT * FROM emp;')
#crhstr = '김태형'
#cursor.execute('SELECT * FROM emp WHERE ename = %s ;' , crhstr)

# 데이타를 하나씩 Fetch하여 출력
#row = cursor.fetchone()

#while row:
    #row = row.encode('ISO-8859-1').decode('euc-kr')
    #print(row[0], row[1].encode('ISO-8859-1').decode('euc-kr'))터
    #print(row['empno'], row['ename'])
    #row = cursor.fetchone()

# 연결 끊기
#cnxn.close()

def call_exec(in_param=[],  func_conn=None, conn=cnxn):
    conn = pymssql.connect(server, username, password, database, charset='utf8')
    # if conn is None and func_conn is not None :
    #     conn = func_conn()
    # if conn is None :
    #     return [None, None]
    cursor = conn.cursor()
    try :
        #cursor.execute('SELECT * FROM emp WHERE ename = %s ;', in_param)
        cursor.execute("SELECT * FROM T_SeatRandomLog", in_param)
        data = cursor.fetchall()

        columns = []
        for c in cursor.description:
            columns.append(c[0])
        return columns, data.encode('ISO-8859-1').decode('euc-kr')
    finally:
        cursor.close()
        conn.close()

def call_procedure_one(procedureName, in_param=[],  func_conn=None, conn=cnxn):
    conn = pymssql.connect(server, username, password, database, charset='utf8')
    print(in_param)
    # if conn is None and func_conn is not None :
    #     conn = func_conn()
    # if conn is None :
    #     return [None, None]
    cursor = conn.cursor()
    try :
        cursor.execute(procedureName, in_param)
        #cursor.callproc(procedureName)
        data = cursor.fetchall()

        columns = []
        for c in cursor.description:
            columns.append(c[0])
        return columns, data
    finally:
        cursor.close()
        conn.close()

def call_procedure_mult(procedureName, in_param=[],  func_conn=None, conn=cnxn):
    conn = pymssql.connect(server, username, password, database, charset='utf8')
    print(in_param)
    # if conn is None and func_conn is not None :
    #     conn = func_conn()
    # if conn is None :
    #     return [None, None]
    cursor = conn.cursor()
    try :
        cursor.executemany(procedureName, in_param)
        #cursor.callproc(procedureName)
        data = cursor.fetchall()

        columns = []
        for c in cursor.description:
            columns.append(c[0])
        return columns, data
    finally:
        cursor.close()
        conn.close()

def call_procedure_tran(procedureName, in_param=[],  func_conn=None, conn=cnxn):
    conn = pymssql.connect(server, username, password, database, charset='utf8')
    print(in_param)
    # if conn is None and func_conn is not None :
    #     conn = func_conn()
    # if conn is None :
    #     return [None, None]
    cursor = conn.cursor()
    try :
        cursor.execute(procedureName, in_param)
        #cursor.callproc(procedureName)
        #cursor.fetchall()
        conn.commit()
    finally:
        cursor.close()
        conn.close()

#obj = call_procedure_mssql('PY_CallTest %s', '김태형')

