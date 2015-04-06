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

namespace SR_file3
{
    public partial class Form1 : Form
    {
        UdpClient udp;
        public Form1()
        {
            InitializeComponent();
            udp = new UdpClient(23333);
        }

        private void Form1_Load(object sender, EventArgs e)
        {
            // Create a new SpeechRecognitionEngine instance.
            sre = new SpeechRecognitionEngine();

            // Create a simple grammar that recognizes "red", "green", or "blue".
            Choices colors = new Choices();

            try//读取文件
            {
                // Create an instance of StreamReader to read from a file.
                // The using statement also closes the StreamReader.
                using (StreamReader sr = new StreamReader("sentences.txt"))
                {
                    String line;
                    // Read and display lines from the file until the end of 
                    // the file is reached.
                    while ((line = sr.ReadLine()) != null)
                    {
                        Console.WriteLine(line);
                        colors.Add(line);
                    }
                }
            }
            catch (Exception ex)
            {
                // Let the user know what went wrong.
                Console.WriteLine("The file could not be read:");
                Console.WriteLine(ex.Message);
            }

            //colors.Add("red");
            //colors.Add("green");
            //colors.Add("blue");

            GrammarBuilder gb = new GrammarBuilder();
            gb.Append(colors);

            // Create the actual Grammar instance, and then load it into the speech recognizer.
            Grammar g = new Grammar(gb);
            sre.LoadGrammar(g);

            // Register a handler for the SpeechRecognized event.
            sre.SpeechRecognized += new EventHandler<SpeechRecognizedEventArgs>(sre_SpeechRecognized);
            sre.SetInputToDefaultAudioDevice();
            sre.RecognizeAsync(RecognizeMode.Multiple);
        }

        // Simple handler for the SpeechRecognized event.
        void sre_SpeechRecognized(object sender, SpeechRecognizedEventArgs e)
        {
            MessageBox.Show(e.Result.Text);
            Byte[] buf = Encoding.ASCII.GetBytes(e.Result.Text);
            udp.Send(buf, buf.Length);
            //Console.WriteLine(e.Result.Text);
        }

        SpeechRecognitionEngine sre;
    }
}
