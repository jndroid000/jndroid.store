import psycopg2

# Connect as postgres
conn = psycopg2.connect(
    host='localhost',
    port=5432,
    user='postgres',
    password='522475',
    database='postgres'
)

conn.autocommit = True
cursor = conn.cursor()

try:
    # Check if user exists
    cursor.execute("SELECT usename FROM pg_user WHERE usename = 'jndroid_user'")
    exists = cursor.fetchone()
    
    if exists:
        print('\n' + '='*70)
        print('ℹ️  User jndroid_user already exists')
        print('='*70)
        print(f'\nUsername: jndroid_user')
        print(f'Status: Ready to use')
    else:
        # Create user
        cursor.execute("CREATE USER jndroid_user WITH PASSWORD '522475'")
        print('\n' + '='*70)
        print('✅ User jndroid_user created successfully')
        print('='*70)
        print(f'\nUsername: jndroid_user')
        print(f'Password: 522475')
        
        # Grant privileges on database
        cursor.execute('GRANT ALL PRIVILEGES ON DATABASE jndroid_db TO jndroid_user')
        print('\n✅ Granted privileges on jndroid_db')
        
except Exception as e:
    if 'already exists' in str(e):
        print('\nℹ️  User already exists')
    else:
        print(f'\n❌ Error: {e}')
finally:
    cursor.close()
    conn.close()
    
print('\n' + '='*70)
print('✅ PostgreSQL User Setup Complete')
print('='*70)
print('\nUser Details:')
print(f'  Host: localhost')
print(f'  Port: 5432')
print(f'  Database: jndroid_db')
print(f'  Username: jndroid_user')
print(f'  Password: 522475')
print('\n' + '='*70)
