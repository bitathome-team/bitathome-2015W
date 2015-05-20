using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;
using System.Speech.Recognition;
using System.IO;
using System.Net.Sockets;
using System.Net;
using System.Collections;


namespace SR_file3
{
    enum status { none, sentences, configs };

    public partial class Form1 : Form
    {
        Socket sock = new Socket(AddressFamily.InterNetwork, SocketType.Dgram, ProtocolType.Udp);
        IPAddress serverAddr;
        IPEndPoint endPoint;

        long last = 0;
        int[] vars = new int[10];
        const long second = 10000000;
        long holdtime = 4 * second;
        ArrayList operations = new ArrayList();

        public Form1()
        {
            InitializeComponent();
            serverAddr = IPAddress.Parse("192.168.0.6");
            endPoint = new IPEndPoint(serverAddr, 23333);
        }

        private void Form1_Load(object sender, EventArgs e)
        {
            // Create a new SpeechRecognitionEngine instance.
            sre = new SpeechRecognitionEngine();

            // Create a simple grammar that recognizes "red", "green", or "blue".
            Choices grammar = new Choices();

            try//读取文件
            {
                OpenFileDialog file = new OpenFileDialog();
                file.Filter = "sentences file|*.txt";
                if (file.ShowDialog() != DialogResult.OK)
                {
                    Application.Exit();
                }
                string sfn = file.FileName;
                status status = status.none;
                this.textBox1.AppendText("sentences file using " + sfn + "\r\nLoading grammar file:\r\n");
                // Create an instance of StreamReader to read from a file.
                // The using statement also closes the StreamReader.
                using (StreamReader sr = new StreamReader(sfn))
                {
                    string line;
                    // Read and display lines from the file until the end of 
                    // the file is reached.
                    while ((line = sr.ReadLine()) != null)
                    {
                        if (line == "" || line[0] == '#')
                        {
                            continue;
                        }
                        if ('[' == line[0])
                        {
                            switch (line)                     // configure type announcement
                            {
                                case "[sentences]":           // for sentences definition, see configure file commont for detail
                                    status = status.sentences;
                                    break;
                                case "[configure]":           // for environment variable definition, see configure file commont for detail
                                    status = status.configs;
                                    break;
                                default:                      // undefined types, announce error and halt
                                    textBox1.AppendText("[Illeagal experesion]: " + line + "\r\n[halt]");
                                    go = true;
                                    break;
                            }
                            continue;
                        }
                        string[] eq = line.Split('!');
                        switch (status)
                        {
                            case status.sentences:                  // when in sentences announcement
                                textBox1.AppendText(eq[0] + "\r\n");// recognition
                                grammar.Add(eq[0]);                 // add to SR
                                string[] op = eq[1].Split(',');     // see configure file commont for detail
                                string[] push = new string[3];
                                push[0] = eq[0];                    // recognition sentence
                                push[1] = op[0];                    // sent sentence
                                push[2] = op[1];                    // operation
                                operations.Add(push);
                                break;
                            case status.configs:
                                switch (eq[0])
                                {
                                    case "holdtime":                // see configure file commont for detail
                                        holdtime = int.Parse(eq[1]) * second;
                                        break;
                                }
                                break;
                            default:                                // undefined variables, announce error and halt
                                textBox1.AppendText("[Illeagal experesion]: " + line + "\r\n[halt]");
                                go = true;
                                break;
                        }
                    }
                }
            }
            catch (Exception ex)
            {
                // Let the user know what went wrong.
                textBox1.AppendText("The file could not be read:");
                textBox1.AppendText(ex.Message);
                go = true;
                return;
            }
            textBox1.AppendText("------------------------------------------------------------\r\n");    // file operation finished.

            GrammarBuilder gb = new GrammarBuilder();
            gb.Append(grammar);

            // Create the actual Grammar instance, and then load it into the speech recognizer.
            Grammar g = new Grammar(gb);
            sre.LoadGrammar(g);

            // Register a handler for the SpeechRecognized event.
            sre.SpeechRecognized += new EventHandler<SpeechRecognizedEventArgs>(sre_SpeechRecognized);
            sre.SetInputToDefaultAudioDevice();
            sre.RecognizeAsync(RecognizeMode.Multiple);

        }

        bool go = false;    // used to sign status of whether halt or not
        // Simple handler for the SpeechRecognized event.
        void sre_SpeechRecognized(object sender, SpeechRecognizedEventArgs RecognitionResult)
        {
            if (go)
            {
                return;
            }
            long now = System.DateTime.Now.Ticks;                      // get present time
            string ret = RecognitionResult.Result.Text;                // get recognition result
            textBox1.AppendText("[" + now + "]: " + ret + "\r\n");     // cout
            if (now - last < holdtime)                                 // if not longer then holdtime then give up the sentence
            {
                return;
            }
            last = now;                                                // update time
            foreach (string[] s in operations)
            {
                if (ret == s[0])
                {
                    exec(s[1], s[2]);
                    break;
                }
            }
        }

        // udp send to server
        void udpsend(string send)
        {
            Byte[] buf = Encoding.ASCII.GetBytes(send + " ");
            sock.SendTo(buf, endPoint);
            textBox1.AppendText("[sent]: " + send + "\r\n");
        }

        // fix execution of one sentence
        void exec(string send, string operation)
        {
            if (" " != send) udpsend(send);     // send part
            if (" " == operation) return;       // operation part
            bool condition = false;
            for (int i = 0; i < operation.Length; i++)
            {
                long temp;
                int num;
                switch (operation[i])
                {
                    case '?':
                        condition = !condition;
                        if (condition)
                        {
                            i = execCondition(operation, ++i);
                            if (i < 0)
                            {
                                i *= -1;
                                for (; operation[i] != '|'; i++) ;
                            }
                            else
                            {
                                i++;
                            }
                        }
                        break;
                    case '|':
                        for (; operation[i] != '?'; i++) ;
                        break;
                    case ';':
                        break;
                    case 's':
                        i = execSend(operation, ++i);
                        break;
                    case 'p':
                        i = execPrint(operation, ++i);
                        break;
                    case 'h':
                        i = execHalt(operation, ++i);
                        break;
                    case '$':
                        {
                            int id = operation[++i] - '0';
                            i += 1;
                            temp = execGetnum(operation, i+2);
                            num = (int)(temp >> 32);
                            switch (operation.Substring(i, 2))
                            {
                                case "+=":
                                    vars[id] += num;
                                    break;
                                case "-=":
                                    vars[id] -= num;
                                    break;
                                case "*=":
                                    vars[id] *= num;
                                    break;
                                case "/=":
                                    vars[id] /= num;
                                    break;
                                case "<-":
                                    vars[id] = num;
                                    break;
                                default:
                                    textBox1.AppendText("[Illeagal experesion]: " + operation + "\r\n[halt]");
                                    go = true;
                                    break;
                            }
                            i = (int)(temp & 0xffffffff);
                        }
                        break;
                    default:
                        textBox1.AppendText("[Illeagal experesion]: " + operation + "\r\n[halt]");
                        go = true;
                        break;
                }
            }
        }

        int execCondition(string operation, int i)
        {
            long temp;
            int num;
            switch (operation[i])
            {
                case 's':
                    i = execSend(operation, ++ i);
                    break;
                case 'p':
                    i = execPrint(operation, ++ i);
                    break;
                case 'h':
                    i = execHalt(operation, ++ i);
                    break;
                case '$':
                    {
                        int id = operation[++i] - '0';
                        switch (operation[++i])
                        {
                            case '>':
                                switch (operation[i + 1])
                                {
                                    case '=':
                                        i += 2;
                                        temp = execGetnum(operation, i);
                                        num = (int)(temp >> 32);
                                        if (vars[id] >= num) i = (int)(temp & 0xffffffff);
                                        else i = -1 * (int)(temp & 0xffffffff);
                                        break;
                                    default:
                                        i++;
                                        temp = execGetnum(operation, i);
                                        num = (int)(temp >> 32);
                                        if (vars[id] > num) i = (int)(temp & 0xffffffff);
                                        else i = -1 * (int)(temp & 0xffffffff);
                                        break;
                                }
                                break;
                            case '<':
                                switch (operation[i + 1])
                                {
                                    case '=':
                                        i += 2;
                                        temp = execGetnum(operation, i);
                                        num = (int)(temp >> 32);
                                        if (vars[id] <= num) i = (int)(temp & 0xffffffff);
                                        else i = -1 * (int)(temp & 0xffffffff);
                                        break;
                                    case '>':
                                        i += 2;
                                        temp = execGetnum(operation, i);
                                        num = (int)(temp >> 32);
                                        if (vars[id] != num) i = (int)(temp & 0xffffffff);
                                        else i = -1 * (int)(temp & 0xffffffff);
                                        break;
                                    default:
                                        i += 2;
                                        temp = execGetnum(operation, i);
                                        num = (int)(temp >> 32);
                                        if (vars[id] > num) i = (int)(temp & 0xffffffff);
                                        else i = -1 * (int)(temp & 0xffffffff);
                                        break;
                                }
                                break;
                            case '=':
                                if ('=' == operation[i + 1])
                                {
                                    i += 2;
                                }
                                else
                                {
                                    i++;
                                }
                                temp = execGetnum(operation, i);
                                num = (int)(temp >> 32);
                                if (vars[id] == num) i = (int)(temp & 0xffffffff);
                                else i = -1 * (int)(temp & 0xffffffff);
                                break;
                            default:
                                textBox1.AppendText("[Illeagal experesion]: " + operation + "\r\n[halt]");
                                go = true;
                                break;
                        }
                    }
                    break;
                default:
                    textBox1.AppendText("[Illeagal experesion]: " + operation + "\r\n[halt]");
                    go = true;
                    break;
            }
            return i;
        }

        long execGetnum(string operation, int i)
        {
            long num = 0;
            if ('$' == operation[i])
            {
                int id = operation[i+1] - '0';
                if (0 <= id && id <= 9)
                {
                    num = vars[id];
                }
                else
                {
                    textBox1.AppendText("[Illeagal experesion]: " + operation + "\r\n[halt]");
                    go = true;
                }
            }
            else if ('0' <= operation[i] && operation[i] <= '9')
            {
                int startIndex = i;
                for (; i < operation.Length && '0' <= operation[i] && operation[i] <= '9'; i++) ;
                num = int.Parse(operation.Substring(startIndex, i - startIndex));
                i--;
            }
            else
            {
                textBox1.AppendText("[Illeagal experesion]: " + operation + "\r\n[halt]");
                go = true;
            }

            long ret = (num << 32) | (long)(i & 0xffffffff);
            return ret;
        }

        int execSend(string operation, int i)
        {
            if ('e' == operation[i] &&
                'n' == operation[i+1] &&
                'd' == operation[i+2] &&
                '(' == operation[i+3])
            {
                int startIndex = i + 4;
                for (i += 4; operation[i] != ')'; i++) ;
                string str = operation.Substring(startIndex, i-startIndex);
                udpsend(str);
            }
            else 
            {
                textBox1.AppendText("[Illeagal experesion]: " + operation + "\r\n[halt]");
                go = true;
            }
            return i;
        }

        int execPrint(string operation, int i)
        {
            if ('r' == operation[i] &&
                'i' == operation[i + 1] &&
                'n' == operation[i + 2] &&
                't' == operation[i + 3] &&
                '(' == operation[i + 4])
            {
                int startIndex = i + 5;
                for (i += 5; operation[i] != ')'; i++) ;
                string str = operation.Substring(startIndex, i - startIndex);
                textBox1.AppendText(str + "\r\n");
            }
            else 
            {
                textBox1.AppendText("[Illeagal experesion]: " + operation + "\r\n[halt]");
                go = true;
            }
            return i;
        }

        int execHalt(string operation, int i)
        {

            if ('a' == operation[i] &&
                'l' == operation[i + 1] &&
                't' == operation[i + 2])
            {
                textBox1.AppendText("[halt]\r\n--------------------------------------------------------------------\r\n");
                go = true;
            }
            else 
            {
                textBox1.AppendText("[Illeagal experesion]: " + operation + "\r\n[halt]");
                go = true;
            }
            return i + 2;
        }

        SpeechRecognitionEngine sre;
    }
}
