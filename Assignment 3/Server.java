import java.io.*;
import java.net.InetAddress;
import java.net.ServerSocket;
import java.net.Socket;
import java.net.UnknownHostException;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Date;
import java.util.List;
import java.util.Scanner;

// Server class for handling single and multi-threaded cases.
public class Server
{
    // Initial number of threads to be initiated.
    private static int noThreads = 0;
    // IP addresses to block.
    static List<String> IPA;
    // The default file to display.
    static String defaultFile;
    private ServerSocket serverSocket;
    private int port;

    public static void main(String [] args) throws IOException
    {
        System.out.print("Welcome To Multi-Server\n");
        System.out.print("Enter (1) To Initiate Single Threaded Server\n");
        System.out.print("Enter (2) To Initiate Multi-Threaded Server\n");
        Scanner input = new Scanner(System.in);
        int flag = input.nextInt();

        if (flag == 1){
            // Question 1
            // Start the single-threaded server.
            Server server = new Server(5001);
            server.serverStart();
        } else if (flag == 2)
        {
            // Question 2
            // Start the multi-threaded server.
            Server server = new Server(5000, "./ConfigurationFile.txt");
            server.startMultiThreadedServer();
        } else
        {
            System.out.print("Wrong Input!! Aborting Procedure!!");
        }
    }

    private static void readConfigFile(String configFile)
    {
        File conf = new File(configFile);
        String configurations = "";
        BufferedReader reader;

        try
        {
            reader = new BufferedReader(new FileReader(conf));
            String line = null;
            while (!(line = reader.readLine()).isEmpty())
            {
                configurations += line + "\n";
            }
            reader.close();
        }
        catch (Exception e){}

        System.out.println(configurations);
        noThreads = Integer.parseInt(configurations.split("\n")[0].split("=")[1]);
        String str = configurations.split("\n")[1].split("=")[1];
        IPA = new ArrayList<String>(Arrays.asList(str.split("\\s*,\\s*")));
        defaultFile = configurations.split("\n")[2].split("=")[1];
    }

    public Server(int port)
    {
        // Question 1
        // Server which does not contain the configuration file.
        this.port = port;
    }

    public Server(int port, String configFile)
    {
        // Question 2
        // Server which contains the configuration file.
        this.port = port;
        Server.readConfigFile(configFile);
    }

    public void startMultiThreadedServer() throws IOException
    {
        serverSocket = new ServerSocket(port);
        System.out.println("Starting Multi-Threaded Server ...");
        
        while (true)
        {
            try
            {
                System.out.println("Waiting for Client .....");
                System.out.println("========================");

                Socket client = serverSocket.accept();
                if (SocketHandler.counter < noThreads)
                {
                    System.out.println("Creating a thread");
                    Thread thread = new Thread(new SocketHandler(client));
                    SocketHandler.counter += 1;
                    thread.start();
                } else
                {
                    BufferedWriter response = new BufferedWriter(new OutputStreamWriter(client.getOutputStream()));
                    StringBuilder sb = new StringBuilder();
                    constructResponseHeader(503, sb);
                    sb.append("The server seems to be full at the moment try later\r\n\r\n");
                    response.write(sb.toString());
                    sb.setLength(0);
                    response.flush();
                    response.close();
                    client.close();
                }
            }
            catch (Exception e)
            {
                e.printStackTrace();
                System.out.println("Exception\n");
            }
        }
    }

    // Function for single-threaded server.
    public void serverStart() throws IOException
    {
        serverSocket = new ServerSocket(port);
        System.out.println("Starting Single-Threaded Server ...");

        try
        {
            System.out.println("Waiting for Client .....");
            System.out.println("=======================");

            Socket client = serverSocket.accept();

            BufferedReader request = new BufferedReader(new InputStreamReader(client.getInputStream()));
            BufferedWriter response = new BufferedWriter(new OutputStreamWriter(client.getOutputStream()));

            String putDataFromClient = "";
            String requestHeader = "";
            String temp = ".";

            while (!temp.equals(""))
            {
                temp = request.readLine();
                System.out.println(temp);
                requestHeader += temp+"\n";
            }
            
            StringBuilder sb = new StringBuilder();
            
            if (requestHeader.split("\n")[0].contains("GET") && checkURL(requestHeader))
            {
                // Get the correct page to display.
                String file = requestHeader.split("\n")[0].split(" ")[1].split("/")[1];
                constructResponseHeader(200, sb);
                response.write(sb.toString());
                response.write(getData(file));
                sb.setLength(0);
                response.flush();
            } else
            {
                // Report Error 404: Page Not Found.
                constructResponseHeader(404, sb);
                response.write(sb.toString());
                response.write(getData("error404.html"));
                sb.setLength(0);
                response.flush();
            }

            request.close();
            response.close();
            client.close();
            serverSocket.close();
            serverStart();
            return;
        }
        catch (Exception i)
        {
            i.printStackTrace();
            System.out.println("Exception\n");
            serverSocket.close();
            serverStart();
        }
    }

    // Function for retrieving the correct file.
    private String getData(String file)
    {
        File myFile = new File(file);
        String responseToClient = "";
        BufferedReader reader;
        System.out.println("Printing the File Path : " + myFile.getAbsolutePath());

        try
        {
            reader = new BufferedReader(new FileReader(myFile));
            String line = null;

            while (!(line = reader.readLine()).contains("</html>"))
            {
                responseToClient += line;
            }

            responseToClient += line;
            reader.close();
        }
        catch (Exception e)
        {
            e.printStackTrace();
            System.out.println("Exception\n");
        }

        return responseToClient;
    }

    // Function to check the integrity of the passed request.
    private static boolean checkURL(String requestHeader)
    {
        String url = requestHeader.split("\n")[0].split(" ")[1].split("/")[1];
        url = ("./" + url);
        boolean exists = new File(url).isFile();
        return exists;
    }

    // Function for returning the correct response header to user request.
    private static void constructResponseHeader(int respondeCode, StringBuilder sb)
    {
        if (respondeCode == 200)
        {
            sb.append("HTTP/1.1 200 OK\r\n");
            sb.append("Date:" + getTimeStamp() + "\r\n");

            try
            {
                sb.append("Server:" + InetAddress.getLocalHost().getHostAddress() + "\r\n");
            }
            catch (UnknownHostException e)
            {
                e.printStackTrace();
                System.out.println("Unknown Host Exception\n");
            }

            sb.append("Content-Type: text/html\r\n");
            sb.append("Connection: Closed\r\n\r\n");
        } else if (respondeCode == 404)
        {
            sb.append("HTTP/1.1 404 Not Found\r\n");
            sb.append("Date:" + getTimeStamp() + "\r\n");

            try
            {
                sb.append("Server:" + InetAddress.getLocalHost().getHostAddress() + "\r\n");
            }
            catch (UnknownHostException e)
            {
                e.printStackTrace();
                System.out.println("Unknown Host Exception\n");
            }

            sb.append("Content-Type: text/html\r\n");
            sb.append("Connection: Closed\r\n\r\n");
        } else
        {
            sb.append("HTTP/1.1 503 Service Unavailable\r\n");
            sb.append("Date:" + getTimeStamp() + "\r\n");

            try
            {
                sb.append("Server:" + InetAddress.getLocalHost().getHostAddress() + "\r\n");
                
            } 
            catch (UnknownHostException e)
            {
                e.printStackTrace();
                System.out.println("Unknown Host Exception\n");
            }

            sb.append("Content-Type: text/html\r\n");
            sb.append("Connection: Closed\r\n\r\n");
        }
    }

    // Function to get the time stamp.
    private static String getTimeStamp()
    {
        Date date = new Date();
        SimpleDateFormat sdf = new SimpleDateFormat("MM/dd/yyyy h:mm:ss a");
        String formattedDate = sdf.format(date);
        return formattedDate;
    }
}