import os
import sys
import shutil
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from psycopg2 import sql
from dotenv import load_dotenv

def setup_database():
    print("=== Khởi tạo CSDL Cổ phiếu (Database) ===")
    
    # 1. Kiểm tra và tạo file .env nếu chưa có
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    env_path = os.path.join(backend_dir, ".env")
    env_example_path = os.path.join(backend_dir, ".env.example")
    
    if not os.path.exists(env_path):
        if os.path.exists(env_example_path):
            print("=> Đang tạo file .env từ template .env.example...")
            shutil.copy(env_example_path, env_path)
        else:
            print("Lỗi: Không tìm thấy cả .env và .env.example!")
            sys.exit(1)
    
    # Tải biến môi trường
    load_dotenv(env_path)
    database_url = os.getenv("DATABASE_URL")
    
    if not database_url:
        print("Lỗi: Không thấy DATABASE_URL cấu hình trong file .env")
        sys.exit(1)

    # 2. Bóc tách thông tin chuỗi kết nối từ DATABASE_URL bằng SQLAlchemy
    try:
        from sqlalchemy.engine.url import make_url
        url = make_url(database_url)
        db_name = url.database
        user = url.username
        password = url.password
        host = url.host
        port = url.port or 5432
    except ImportError:
        print("Lỗi: Không import được sqlalchemy. Vui lòng chạy pip install sqlalchemy trước.")
        sys.exit(1)
    except Exception as e:
        print(f"Lỗi cú pháp DATABASE_URL: {e}")
        sys.exit(1)

    # 3. Tạo Database bằng psycopg2 (kết nối đến CSDL postgres mặc định)
    try:
        print(f"=> Đang kết nối vào máy chủ PostgreSQL tại {host}:{port} với user '{user}'...")
        conn = psycopg2.connect(
            dbname="postgres",
            user=user,
            password=password,
            host=host,
            port=port
        )
        # Bắt buộc đặt AUTOCOMMIT để thực thi lệnh CREATE DATABASE
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Kiểm tra xem Database đã tồn tại chưa
        cursor.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = %s", (db_name,))
        exists = cursor.fetchone()
        
        if not exists:
            print(f"=> Database '{db_name}' chưa có. Tiến hành tạo mới...")
            # Sử dụng sql.Identifier để query Create DataBase an toàn
            cursor.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(db_name)))
            print(f"-> Tạo Database '{db_name}' thành công!")
        else:
            print(f"-> Database '{db_name}' đã tồn tại sẵn. Bỏ qua bước tạo.")
            
        cursor.close()
        conn.close()
        
    except psycopg2.OperationalError as e:
        print(f"\n[!] Lỗi khi kết nối đến PostgreSQL:\n{e}")
        print("Gợi ý: Hãy chắc chắn máy nhà bạn đã cài và đang BẬT PostgreSQL (VD: service đang chạy), đồng thời thông tin Username và Password trong .env là ĐÚNG.")
        sys.exit(1)
    except Exception as e:
        print(f"\n[!] Có lỗi không mong muốn khi tạo database: {e}")
        sys.exit(1)

    # 4. Chạy Alembic Migration để tạo cấu trúc Băng (Tables)
    print("\n=> Đang chạy Alembic Migration để khởi tạo các Bảng trong CSDL...")
    
    # Chuyển thư mục về backend để lệnh alembic có thể tham chiếu alembic.ini chính xác
    os.chdir(backend_dir)
    
    # Tạo folder versions nếu chưa có
    versions_dir = os.path.join(backend_dir, "alembic", "versions")
    if not os.path.exists(versions_dir):
        os.makedirs(versions_dir)
        
    # Tạo tự động 1 file revision nếu chưa có bất kỳ file migration nào
    migration_files = [f for f in os.listdir(versions_dir) if f.endswith(".py")]
    if len(migration_files) == 0:
        print("=> Không tìm thấy migration hiện tại. Tự động sinh file migration đầu tiên...")
        os.system('alembic revision --autogenerate -m "Init Database"')

    # Thực thi lệnh nâng cấp DB bằng Python system call
    exit_code = os.system("alembic upgrade head")
    
    if exit_code == 0:
        print("\n=== HOÀN TẤT THIẾT LẬP BẢNG ===")
        print("=> CSDL đã sẵn sàng để hoạt động!")
    else:
        print("\n[!] Lỗi: Lệnh tạo bảng (alembic) gặp thất bại. Vui lòng xem log ở trên.")
        sys.exit(1)

if __name__ == "__main__":
    setup_database()
