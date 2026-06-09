# PyMySQL compatibility layer for MySQL backend
# Only import when available (local dev uses MySQL, Vercel/production uses PostgreSQL)
try:
    import pymysql
    pymysql.install_as_MySQLdb()
except ImportError:
    pass  # PostgreSQL (Supabase) doesn't need PyMySQL
