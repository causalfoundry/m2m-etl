import os

if __name__ == '__main__':
    print('ETL starting')
    for key, value in os.environ.items():
        if key.startswith("ETL_"):
            print(f"{key}: {value}")
