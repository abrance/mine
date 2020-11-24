#include <stdio.h>
#include <arpa/inet.h>
#include <string.h>
#include <sys/socket.h>
#include <unistd.h>
#include <stdlib.h>

#define BUFFER_SIZE 1024

int main(){
  char listen_addr_str[] = "0.0.0.0";
  size_t listen_addr = inet_addr(listen_addr_str);
  int port = 8080;
  int server_socket, client_socket;
  struct sockaddr_in server_addr, client_addr;
  socklen_t addr_size;
  char buffer[BUFFER_SIZE]; // 缓冲区大小
  
  int str_length;
  server_socket = socket(PF_INET, SOCK_STREAM, 0); // 创建socket PF_INET 等同于AF_INET

  bzero(&server_addr, sizeof(server_addr)); // 初始化
  server_addr.sin_family = INADDR_ANY;
  server_addr.sin_port = htons(port);
  server_addr.sin_addr.s_addr = listen_addr;

  if (bind(server_socket, (struct sockaddr *) &server_addr, sizeof(server_addr)) == -1) {
    printf("绑定失败\n");
    exit(1);
  }
  if (listen(server_socket, 5) == -1) {
    printf("监听失败\n");
    exit(1);
  }

  printf("创建TCP 服务成功\n");
  addr_size = sizeof(client_addr);
  client_socket = accept(server_socket, (struct sockaddr *) &client_addr, &addr_size);
  printf("%d 连接成功\n", client_socket);
  char msg[] = "连接成功";
  write(client_socket, msg, sizeof(msg));

  while (1) {
    str_length = read(client_socket, buffer, BUFFER_SIZE);
    if (str_length == 0) {
      close(client_socket);
      printf("连接已关闭： %d\n", client_socket);
      break;
    } else{
      printf("客户端发送数据： %s", buffer);
      write(client_socket, buffer, str_length); // 发送数据
    }
  }

  return 0;
}
