using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Net.Sockets;
using System.Net;

namespace udp_send
{
    class Program
    {
        static void Main(string[] args)
        {
            Socket sock = new Socket(AddressFamily.InterNetwork, SocketType.Dgram, ProtocolType.Udp);
            IPAddress serverAddr;
            IPEndPoint endPoint;
            serverAddr = IPAddress.Parse("192.168.0.6");
            endPoint = new IPEndPoint(serverAddr, 23333);
            while (true)
            {
                string str = Console.ReadLine() + " ";
                Byte[] buf = Encoding.ASCII.GetBytes(str);
                sock.SendTo(buf, endPoint);
            }
        }
    }
}
