import java.io.*;
import java.net.InetAddress;
import java.net.Socket;
import java.net.UnknownHostException;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.concurrent.TimeUnit;

// Class for handling the multi-threaded scenario.
public class SocketHandler implements Runnable
{
    // Data members of the class.
    public static int counter = 0;
    private Socket client;

    // Function for initializing the client member of the class.
    public SocketHandler(Socket client)
    {
        this.client = client;
    }

    // Function for running the threaded out execution of the socket.
    public void run()
    {
        System.out.println("Threaded out for client : " + client.toString() + " with thread id as : " + Thread.currentThread().getName());

        try
        {
            TimeUnit.SECONDS.sleep(10);
            processClient();
        }
        catch (IOException | InterruptedException e) 
        {
            e.printStackTrace();
        }
    }

    // Function for processing the client request.
    private void processClient() throws IOException
    {
        try
        {
            BufferedReader request = new BufferedReader(new InputStreamReader(client.getInputStream()));
            BufferedWriter response = new BufferedWriter(new OutputStreamWriter(client.getOutputStream()));

            String putDataFromClient = "";
            String requestHeader = "";
            String temp = ".";

            while (!temp.equals(""))
            {
                temp = request.readLine();
                requestHeader += temp + "\n";
            }

            System.out.print("The header from thread id : " + Thread.currentThread().getName()  + "is" + "\n" + requestHeader);

            // Now we will process the header.
            // String builder will contain our response.
            StringBuilder sb = new StringBuilder();

            if (checkClientValidity())
            {
                // If client is not blocked, grant access.
                if (requestHeader.split("\n")[0].contains("GET") && checkURL(requestHeader))
                {
                    // Get the correct page to display.
                    String file;
                    if (requestHeader.split("\n")[0].split(" ")[1].equals("/"))
                    {
                        file = "/";
                    } else
                    {
                        file = requestHeader.split("\n")[0].split(" ")[1].split("/")[1];
                    }
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
                    response.close();
                    client.close();
                }
            } else
            { 
                // If the IP address is blocked, send a request for denial of service.
                constructResponseHeader(403, sb);
                response.write(sb.toString());
                sb.setLength(0);
                response.flush();
                response.close();
                client.close();
            }
        }
        catch(Exception e){
            e.printStackTrace();
        }

        client.close();
        counter -= 1;
    }

    // Function to check the validity of the passed request.
    private boolean checkClientValidity()
    {
        // Server.IPA contains the IP address to be blocked
        String addressOfClient = client.getInetAddress().getHostAddress();
        return !Server.IPA.contains(addressOfClient);
    }

    // Function to check the integrity of the passed request.
    private static boolean checkURL(String header)
    {
        String url = header.split("\n")[0].split(" ")[1];
        if (url.equals("/"))
        {
            return true;
        }

        url = header.split("\n")[0].split(" ")[1].split("/")[1];
        url = ("./" + url);
        boolean exists = new File(url).isFile();
        return exists;
    }

    // Function for retrieving the correct file.
    private static String getData(String file)
    {
        if (file.equals("/"))
        {
            file = Server.defaultFile;
        }

        File myFil = new File(file);
        // Extract the html file to respond to client.
        String responseToClient = "";
        BufferedReader reader;

        System.out.println("Printing the file path : " + myFil.getAbsolutePath());

        try
        {
            reader = new BufferedReader(new FileReader(myFil));
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
            System.out.println("File Reading Exception");
        }

        return responseToClient;
    }

    // Function for returning the correct response header to user request.
    private void constructResponseHeader(int respondeCode, StringBuilder sb)
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
                System.out.println("Unknown Host Exception");
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
                System.out.println("Unknown Host Exception");
            }

            sb.append("Content-Type: text/html\r\n");
            sb.append("Connection: Closed\r\n\r\n");
        } else
        {
            sb.append("HTTP/1.1 403 Forbidden\r\n");
            sb.append("Date:" + getTimeStamp() + "\r\n");

            try
            {
                sb.append("Server:" + InetAddress.getLocalHost().getHostAddress() + "\r\n");
            } 
            catch (UnknownHostException e)
            {
                e.printStackTrace();
                System.out.println("Unknown Host Exception");
            }

            sb.append("Content-Type: text/html\r\n");
            sb.append("Connection: Closed\r\n\r\n");
        }

        System.out.println(sb);
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