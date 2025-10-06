import logging

file_path = "json/recordedIndex.txt"

index_set = set()

try:
    with open(file_path, "r", encoding="utf-8") as file:
        for line in file:
            indexArray = line.strip().split(",")
            for index in indexArray:
                index_set.add(index)


except FileNotFoundError:
    print(f"错误：文件 '{file_path}' 不存在")
except Exception as e:
    print(f"读取错误：{e}")

def append_index_set(input_set: set):
    with open(file_path, "a", encoding="utf-8") as append_file:
        append_file.write("\n")
        append_file.write(",".join(input_set))




if __name__ == '__main__':
    print("read test: ")
    print(index_set)

    test_set = set()
    test_set.add("number1")
    test_set.add("number2")
    append_index_set(test_set)
