# mssql-python-pyodbc
# Python runtime with pyodbc to connect to SQL Server
FROM paolamedo/dash-sql-azure:v1

WORKDIR .
ADD . .

# Make port 8050 available to the world outside this container
EXPOSE 8050

ENTRYPOINT [ "python3" ]
CMD ["app.py"]
