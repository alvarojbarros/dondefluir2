from tools.DBVersion import DBVersion
import settings
from tools.dbconnect import Session

session = Session()
record = session.query(DBVersion).first()
version = record.Version
if not settings.versions:
    newVersion = 1
else:
    newVersion = max(sorted(settings.versions))
for k in range(version,newVersion):
    if k+1 in settings.versions:
        for sql in settings.versions[k+1]:
            session.execute(sql)
    record.Version = newVersion
    session.commit()
session.close()