import os
import csv
import argparse
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom

def prettify(elem):
    """返回格式化后的XML字符串。"""
    rough_string = tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="\t")

def generate_xml_content(data):
    """生成CDL文件的XML内容。"""
    # 解析ASC_SOP字段，移除括号并分割为单独的数值
    sop_values = data['ASC_SOP'].replace(')(', ' ').replace('(', '').replace(')', '').split()
    slope_values = sop_values[:3]
    offset_values = sop_values[3:6]
    power_values = sop_values[6:9]

    # 创建ColorDecisionList元素
    color_decision_list = Element('ColorDecisionList')
    color_decision_list.set('xmlns', "urn:ASC:CDL:v1.01")

    # 创建并填充ColorDecision和ColorCorrection元素
    color_decision = SubElement(color_decision_list, 'ColorDecision')
    color_correction = SubElement(color_decision, 'ColorCorrection')
    
    # 创建并填充SOPNode
    sop_node = SubElement(color_correction, 'SOPNode')
    description = SubElement(sop_node, 'Description')
    # 移除文件名中的扩展名
    description.text = os.path.splitext(data['Name'])[0]
    slope = SubElement(sop_node, 'Slope')
    slope.text = ' '.join(slope_values)
    offset = SubElement(sop_node, 'Offset')
    offset.text = ' '.join(offset_values)
    power = SubElement(sop_node, 'Power')
    power.text = ' '.join(power_values)
    
    # 创建并填充SATNode
    sat_node = SubElement(color_correction, 'SATNode')
    saturation = SubElement(sat_node, 'Saturation')
    saturation.text = data['ASC_SAT']

    return prettify(color_decision_list).split('\n', 1)[1]  # 移除XML声明

def parse_ale_file(file_path):
    """解析ALE文件并提取所需数据。"""
    data = []
    headers = []
    reading_data = False

    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            # 跳过注释和空行
            if line.startswith('#') or not line.strip():
                continue
            # 检测到列头定义行，开始读取数据
            if 'Name' in line:
                headers = line.strip().split('\t')
                reading_data = True
                continue
            # 开始读取实际的数据行
            if reading_data:
                values = line.strip().split('\t')
                if len(values) == len(headers):
                    # 将列头和数据行组合为字典
                    data.append(dict(zip(headers, values)))
    return data

def generate_cdl_files( , output_directory):
    """根据ALE文件生成CDL文件，并将它们存放在指定输出目录下的文件夹中。"""
    # 获取输入文件的文件名（不带扩展名）以创建输出文件夹
    ale_filename = os.path.splitext(os.path.basename(ale_file_path))[0]
    final_output_directory = os.path.join(output_directory, ale_filename)
    os.makedirs(final_output_directory, exist_ok=True)

    # 解析ALE文件并生成CDL文件
    ale_data = parse_ale_file(ale_file_path)
    for data in ale_data:
        xml_content = generate_xml_content(data)
        # 移除文件名中的扩展名，用于创建输出文件名
        file_name_without_extension = os.path.splitext(data['Name'])[0]
        file_name = f'{file_name_without_extension}.cdl'
        # 创建最终的文件路径
        file_path = os.path.join(final_output_directory, file_name)
        # 写入CDL文件内容
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write('<?xml version="1.0" encoding="UTF-8"?>\n')
            file.write(xml_content)
        print(f'Generated {file_path}')

if __name__ == '__main__':
    # 创建ArgumentParser的实例
    parser = argparse.ArgumentParser(description='Generate CDL files from an ALE file.')
    # 添加-i参数，用于指定输入文件的路径
    parser.add_argument('-i', '--input', help='Path to the input ALE file.')
    # 添加-o参数，用于指定输出目录的路径
    parser.add_argument('-o', '--output', help='Directory where CDL files will be saved.')
    
    # 解析命令行参数
    args = parser.parse_args()

    # 设置默认输入和输出路径
    # default_input_file = "/path/to/default/input_file.ale"  # 请根据需要修改默认路径
    default_output_dir = os.path.dirname(default_input_file)  # 默认输出目录为输入文件所在目录

    # # 如果命令行参数未提供输入路径，则使用默认路径
    # input_file_path = os.path.abspath(args.input) if args.input else default_input_file
    # 如果命令行参数未提供输出路径，则使用输入文件所在目录
    output_directory = os.path.abspath(args.output) if args.output else os.path.dirname(input_file_path)

    # 确保输入文件存在
    if not os.path.exists(input_file_path):
        print(f"输入文件未找到：{input_file_path}")
    else:
        # 执行转换
        generate_cdl_files(input_file_path, output_directory)