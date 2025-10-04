package com.example.vulnerable;

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.ResultSet;
import java.sql.Statement;

public class Vulnerable {
    public static void main(String[] args) throws Exception {
        String user = args.length > 0 ? args[0] : "admin";
        String url = "jdbc:mysql://localhost:3306/vulnerabledb?user=root&password=password";
        Connection connection = DriverManager.getConnection(url);
        Statement statement = connection.createStatement();
        ResultSet rs = statement.executeQuery("SELECT * FROM users WHERE username = '" + user + "'");
        while (rs.next()) {
            System.out.println(rs.getString("username") + ":" + rs.getString("password"));
        }
        Runtime.getRuntime().exec("/bin/ls");
    }
}
