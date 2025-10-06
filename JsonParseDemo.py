import json

json_file_path = "json/data.json"

# 读取 JSON 文件并转换为字典数组
try:
    with open(json_file_path, "r", encoding="utf-8") as f:
        dict_array = json.load(f)

except FileNotFoundError:
    print(f"错误：未找到文件 {json_file_path}，请检查路径是否正确")
except json.JSONDecodeError:
    print("错误：JSON 文件格式无效，请检查文件内容是否符合标准 JSON 格式")
except Exception as e:
    print(f"其他错误：{e}")

if __name__ == "__main__":
    #  验证结果
    print("第一个笔记的desc：", dict_array[0]["desc"])