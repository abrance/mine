# # -*- coding: utf-8 -*-
#
# # 接收用户的输入，运行特定的测试
#
# import struct
# import json
# import hashlib
#
# import config
# import utils
# import packet
#
#
# g_transaction_id = 0
# g_sequence_id = 0
#
# def send_upload_start_request(clisock, filename):
#     md5 = hashlib.md5()
#     with open(filename) as f:
#         md5.update(f.read())
#     msg = packet.Message()
#     msg.taskinfo.app_id = config.c.app_id
#     msg.taskinfo.sgw_ip = ?
#     msg.taskinfo.file_md5 = md5.hexdigest()
#     msg.taskinfo.file_name = __file__
#     msg.header.command = config.SGW_UPLOAD_START_REQ
#     msg.header.dst_type = config.SGW_TYPE
#     msg.header.dst_id = config.c.dst_sgw_id
#     msg.tranid = g_transaction_id; g_transaction_id = g_transaction + 1
#     msg.sequence = g_sequence_id; g_sequence_id = g_sequence_id + 1
#     clisock.sendall(msg.pack())
#
# def send_upload_data_request(clisock, filename):
#     file_size = os.stat(filename).st_size
#     total_read = 0
#     with open(filename) as f:
#         while True:
#             chunk = f.read(4096)
#             if chunk:
#                 chunk_len = len(chunk)
#                 total_read = total_read + chunk_len
#                 # 读取了文件内容，构造消息包，填充内容然后发送
#                 msg = packet.Message()
#                 msg.header.command = config.SGW_UPLOAD_DATA_REQ
#                 msg.header.dst_type = config.SGW_TYPE
#                 msg.header.dst_id = config.c.dst_sgw_id
#             else:
#                 if total_read < file_size:
#                     print("total read ({}) < file size ({})".format(
#                         total_read, chunk_len
#                     ))
#                     return False
#                 break
#
# def send_upload_file(filename):
#     clisock = utils.create_client_socket(config.c.mds_ip, config.c.mds_port)
#     send_upload_start_request(clisock, filename)
#
#     response = utils.attempt_recvall(clisock, ?)
#     msg = packet.unpack(response)
#     if msg.header.command == config.SGW_UPLOAD_START_RSP:
#         if msg.header.ack_code == 200:
#             # 开始上传请求成功，接下来进行文件内容的传输
#             pass
#         else:
#             print("upload file {} failed: ack_code={}".format(
#                 filename, msg.header_ack_code
#             ))
#             clisock.close()
#             return False
#     else:
#         print("wrong response type: {}".format(msg.header.command))
#         clisock.close()
#         return False
#
# def t1_sgw_upload_and_download():
#     # 1. 上传一个真实的文件
#     # 2. 下载一个真实的文件
#     # 3. 校验 md5sum/cmp
#     send_upload_file(os.path.abspath(__file__))
#
#     # 2. 下载
#
#     # 3. 校验
#
# def t1_client_upload_and_download():
#     # 1. 上传一个真实的文件
#     # 2. 下载一个真实的文件
#     # 3. 校验 md5sum/cmp
#     file_to_upload = os.path.abspath(__file__)
#     md5 = hashlib.md5()
#     with open(file_to_upload) as f:
#         md5.update(f.read())    # 嗯，简单粗暴了一点，毕竟这种测试不考虑性能
#     md5sum = md5.hexdigest()
#
#     msg = packet.Message()
#     msg.header.command = config.CLIENT_UPLOAD
#     msg.header.dst_type = config.METADATA_TYPE
#     msg.header.dst_id = config.c.dst_mds_id
#     msg.tranid = g_transaction_id
#     msg.sequence = g_sequence_id
#     g_transaction_id = g_transaction_id + 1
#     g_sequence_id = g_sequence_id + 1
#
# def test_client_upload():
#     args_filepath = input("request(json absolute filepath): ")
#     with open(args_filepath) as fin:
#         file_blocks_unpack = json.load(fin)
#         print(json.dumps(file_blocks_unpack, indent=4, ensure_ascii=False))
#
#     file_path = file_blocks_unpack["file_path"].encode("utf-8")
#     file_name = file_blocks_unpack["file_name"].encode("utf-8")
#     file_md5  = file_blocks_unpack["file_md5"].encode("utf-8")
#     region_id = file_blocks_unpack["region_id"]
#     site_id   = file_blocks_unpack["site_id"]
#     app_id    = file_blocks_unpack["app_id"]
#     timestamp = file_blocks_unpack["timestamp"]
#     del file_blocks_unpack["file_name"]
#     del file_blocks_unpack["file_md5"]
#     del file_blocks_unpack["region_id"]
#     del file_blocks_unpack["site_id"]
#     del file_blocks_unpack["app_id"]
#     del file_blocks_unpack["timestamp"]
#
#     file_blocks_pack = json.dumps(file_blocks_unpack).encode("utf-8")
#     meta_size = len(file_blocks_pack)
#     body_size = struct.calcsize(config.Constant.FMT_TASKINFO_FIXED)
#     head_size = struct.calcsize(config.Constant.FMT_COMMON_HEAD)
#
#     # header
#     t_header = Header()
#     t_header.command = config.Constant.CLIENT_UPLOAD
#     t_header.total_size = head_size + body_size + meta_size
#     header_pack = t_header.pack()
#
#     # body
#     t_body = Body()
#     t_body.file_name = file_name
#     t_body.file_md5  = file_md5
#     t_body.region_id = region_id
#     t_body.site_id = site_id
#     t_body.app_id = app_id
#     t_body.timestamp = timestamp
#     t_body.metadata_len = meta_size
#     body_pack = t_body.pack()
#
#     # the whole packet
#     pkt = header_pack + body_pack + file_blocks_pack
#
#     # send and recv message
#     host = input("host: ")
#     port = input("port: ")
#     clisock = utils.create_client_socket(host, int(port))
#     clisock.sendall(pkt)
#
#     recvlen, header_pack = utils.attempt_recvall(clisock, config.Constant.HEAD_LENGTH)
#
#     if recvlen == config.Constant.HEAD_LENGTH:
#         header_unpack = struct.unpack(config.Constant.FMT_COMMON_HEAD,
#                                       header_pack)
#         ack_code = header_unpack[10]
#         if int(ack_code) == 200:
#             print("test_client_upload: OK")
#         else:
#             print("test_client_upload: FAIL (ack={0})".format(ack_code))
#     else:
#         print("test_client_upload: FAIL (recv uncompleted packet)")
#
#     clisock.close()
#
#
# def test_client_query_file_number():
#     args_filepath = input("request(json absolute filepath): ")
#     with open(args_filepath) as fin:
#         query_body_unpack = json.load(fin)
#         print(json.dumps(query_body_unpack, indent=4, ensure_ascii=False))
#     query_body_pack = json.dumps(query_body_unpack).encode("utf-8")
#     query_body_size = len(query_body_pack)
#
#     head_size = struct.calcsize(config.Constant.FMT_COMMON_HEAD)
#     total_size = head_size + query_body_size
#
#     # header
#     t_header = Header()
#     t_header.total_size = total_size
#     t_header.command = config.Constant.CLIENT_QUERY_NUM
#     header_pack = t_header.pack()
#
#     # packet
#     pkt = header_pack + query_body_pack
#
#     # send request
#     host = input("host: ")
#     port = input("port: ")
#     clisock = utils.create_client_socket(host, int(port))
#     clisock.sendall(pkt)
#
#     # recv response
#     recvlen, header_pack = utils.attempt_recvall(clisock,
#                                                  config.Constant.HEAD_LENGTH)
#     if recvlen == config.Constant.HEAD_LENGTH:
#         header_unpack = struct.unpack(config.Constant.FMT_COMMON_HEAD,
#                                       header_pack)
#         print("nr_files:", header_unpack[11])
#         print("test_client_query_file_num: OK")
#     else:
#         print("test_client_query_file_num: FAIL (recv uncompleted message)")
#
#
# def test_client_query_file_data():
#     args_filepath = input("request(json absolute filepath): ")
#     with open(args_filepath) as fin:
#         query_body_unpack = json.load(fin)
#         print(json.dumps(query_body_unpack, indent=4, ensure_ascii=False))
#     query_body_pack = json.dumps(query_body_unpack).encode('utf-8')
#     query_body_size = len(query_body_pack)
#
#     head_size = struct.calcsize(config.Constant.FMT_COMMON_HEAD)
#     total_size = head_size + query_body_size
#
#     # header
#     t_header = Header()
#     t_header.total_size = total_size
#     t_header.command = config.Constant.CLIENT_QUERY_DATA
#     header_pack = t_header.pack()
#
#     # packet
#     pkt = header_pack + query_body_pack
#
#     # send request
#     host = input("host: ")
#     port = input("port: ")
#     clisock = utils.create_client_socket(host, int(port))
#     clisock.sendall(pkt)
#
#     def parse(entry):
#         fixlen = struct.calcsize(config.Constant.FMT_TASKINFO_FIXED)
#         body_pack = entry[:fixlen]
#         body_unpack = struct.unpack(config.Constant.FMT_TASKINFO_FIXED,
#                                     body_pack)
#         metalen = body_unpack[15]
#         return (fixlen, metalen)
#
#     def output(meta_unpack):
#         print("user_id:", meta_unpack.get("user_id"))
#         print("customer_id:", meta_unpack.get("customer_id"))
#         print("file_path:", meta_unpack.get("file_path"))
#         print("file_name:", meta_unpack.get("file_name"))
#         print("file_md5:", meta_unpack.get("file_md5"))
#         print("thumb_md5", meta_unpack.get("thumb_md5"))
#         print("nr_blocks:", meta_unpack.get("nr_blocks"))
#         blocks = meta_unpack.get("blocks")
#         for block_id, block_md5 in enumerate(blocks):
#             print("block: {0} {1} {2}".format(
#                 block_id, block_md5, meta_unpack.get(block_md5)
#             ))
#         print("auto_examine:", meta_unpack.get("auto_examine"))
#         print("text:", meta_unpack.get("text"))
#         examine_details = meta_unpack.get("examine_details")
#         if examine_details:
#             for detail in examine_details:
#                 print("word: {0}, time: {1}".format(
#                     detail.get("word"), detail.get("time")
#                 ))
#
#     def parse_and_output(pkt):
#         while len(pkt) > 0:
#             fixlen, metalen = parse(pkt)
#
#             meta_pack = pkt[fixlen:fixlen+metalen]
#             meta_unpack = json.loads(meta_pack.decode('utf-8'))
#
#             output(meta_unpack)
#
#             pkt = pkt[fixlen+metalen:]
#
#
#     # recv response
#     hdrlen, header_unpack, bodylen, body_pack = utils.get_msg(
#         clisock, config.Constant.HEAD_LENGTH, config.Constant.FMT_COMMON_HEAD
#     )
#     if header_unpack:
#         ack_code = header_unpack[10]
#         if int(ack_code) == 200:
#             if body_pack:
#                 parse_and_output(body_pack)
#                 print("test_client_query_data: OK")
#             else:
#                 print("test_client_query_data: OK (no file metadata)")
#         else:
#             print("test_client_query_file_data: FAIL (ack={0})".format(
#                 ack_code))
#     else:
#         print("test_client_query_file_data: FAIL (uncompleted header)")
#
#
# def test_client_delete():
#     args_filepath = input("request(json absolute filepath): ")
#     with open(args_filepath) as fin:
#         query_body_unpack = json.load(fin)
#         print(json.dumps(query_body_unpack, indent=4, ensure_ascii=False))
#
#     site_id = query_body_unpack.get("site_id")
#     app_id = query_body_unpack.get("app_id")
#     timestamp = query_body_unpack.get("timestamp")
#     file_name = query_body_unpack.get("file_name").encode("utf-8")
#     file_md5  = query_body_unpack.get("file_md5").encode("utf-8")
#
#     # body
#     t_body = Body()
#     t_body.site_id = int(site_id)
#     t_body.app_id = int(app_id)
#     t_body.timestamp = int(timestamp)
#     t_body.file_name = file_name
#     t_body.file_md5 = file_md5
#     body_pack = t_body.pack()
#     body_size = len(body_pack)
#
#     # meta
#     del query_body_unpack["site_id"]
#     del query_body_unpack["app_id"]
#     del query_body_unpack["timestamp"]
#     del query_body_unpack["file_name"]
#     del query_body_unpack["file_md5"]
#     query_body_pack = json.dumps(query_body_unpack).encode("utf-8")
#     query_body_size = len(query_body_pack)
#
#     # header
#     t_header = Header()
#     t_header.command = config.Constant.CLIENT_DEL
#     head_size = struct.calcsize(config.Constant.FMT_COMMON_HEAD)
#     t_header.total_size = head_size + body_size + query_body_size
#     header_pack = t_header.pack()
#
#     # packet
#     pkt = header_pack + body_pack + query_body_pack
#
#     # send request
#     host = input("host: ")
#     port = input("port: ")
#     clisock = utils.create_client_socket(host, int(port))
#     clisock.sendall(pkt)
#
#     # recv response
#     recvlen, header_pack = utils.attempt_recvall(clisock,
#                                                  config.Constant.HEAD_LENGTH)
#     if recvlen == config.Constant.HEAD_LENGTH:
#         header_unpack = struct.unpack(config.Constant.FMT_COMMON_HEAD,
#                                       header_pack)
#         ack_code = header_unpack[10]
#         if int(ack_code) == 200:
#             print("test_client_delete: OK")
#         else:
#             print("test_client_delete: FAIL (ack={0})".format(ack_code))
#     else:
#         print("test_client_delete: FAIL (recv uncompleted message)")
#
#
# def test_migration_start():
#     args_filepath = input("request(json absolute filepath): ")
#     with open(args_filepath) as fin:
#         migoption = json.load(fin)
#         print(json.dumps(migoption, indent=4, ensure_ascii=False))
#
#     old_sgw_ip   = migoption.get("old_sgw_ip").encode("utf-8")
#     old_sgw_port = migoption.get("old_sgw_port")
#     new_sgw_ip   = migoption.get("new_sgw_ip").encode("utf-8")
#     new_sgw_port = migoption.get("new_sgw_port")
#     old_mds_ip   = migoption.get("old_mds_ip").encode("utf-8")
#     old_mds_port = migoption.get("old_mds_port")
#     new_mds_ip   = migoption.get("new_mds_ip").encode("utf-8")
#     new_mds_port = migoption.get("new_mds_port")
#
#     # payload
#     fmt_migoption = "!64sH64sH64sH64sH"
#     migoption_unpack = (
#         old_sgw_ip, old_sgw_port, new_sgw_ip, new_sgw_port,
#         old_mds_ip, old_mds_port, new_mds_ip, new_mds_port
#     )
#     migoption_pack = struct.pack(fmt_migoption, *migoption_unpack)
#     print("migoption_pack size: ", struct.calcsize(fmt_migoption))
#     print("migoption_pack len:  ", len(migoption_pack))
#
#     # Header
#     t_header = Header()
#     t_header.total_size = 64 + len(migoption_pack)
#     t_header.command = 0x00030001
#     header_pack = t_header.pack()
#
#     # packet
#     pkt = header_pack + migoption_pack
#
#     # send request to sgw
#     clisock = utils.create_client_socket(old_sgw_ip, old_sgw_port)
#     clisock.sendall(pkt)
#
#     # recv response
#     recvlen, header_pack = utils.attempt_recvall(
#         clisock, config.Constant.HEAD_LENGTH
#     )
#     if recvlen == config.Constant.HEAD_LENGTH:
#         header_unpack = struct.unpack(
#             config.Constant.FMT_COMMON_HEAD, header_pack
#         )
#         ack_code = header_unpack[10]
#         if int(ack_code) == 200:
#             print("test_migration_start: OK")
#         else:
#             print("test_migration_start: FAIL (ack={0})".format(ack_code))
#     else:
#         print("test_migration_start: FAIL (recv uncompleted message)")
#
# def quit():
#     sys.exit(0)
