import pymysql
c=pymysql.connect(host='localhost',port=3306,user='root',password='200486qq.',database='novel_fiction',charset='utf8mb4')
r=c.cursor()

batches = [
    (88, 97, '都市'),
    (98, 107, '穿越'),
    (108, 117, '科幻'),
    (118, 127, '游戏'),
    (138, 147, '悬疑'),
    (148, 155, '武侠'),
    (156, 165, '历史'),
]

total = 0
for start, end, cat in batches:
    sql = f"UPDATE novel SET category=%s, tags=%s WHERE id BETWEEN %s AND %s"
    r.execute(sql, (cat, cat, start, end))
    c.commit()
    cnt = r.rowcount
    total += cnt
    print(f'  ID {start:3d}-{end:3d} -> {cat} ({cnt} books)')

print(f'\nDone! {total} categories updated.')

r.execute('SELECT category, COUNT(*) FROM novel WHERE id>=88 GROUP BY category ORDER BY COUNT(*) DESC')
print('\nCategory distribution:')
for row in r.fetchall():
    print(f'  {row[0]:4s}: {row[1]} books')
c.close()
