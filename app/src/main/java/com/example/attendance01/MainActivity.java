package com.example.attendance01;

import androidx.appcompat.app.AppCompatActivity;

import android.content.Intent;
import android.os.Bundle;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.Toast;

public class MainActivity extends AppCompatActivity {

    private  EditText etUserid;
    private EditText etPswd;
    private Button Btn;
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        etUserid = (EditText) findViewById(R.id.et_userid);
        etPswd = (EditText) findViewById(R.id.et_pswd);
        Btn = (Button) findViewById(R.id.btn);
        Btn.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                validate(etUserid.getText().toString(),etPswd.getText().toString());
            }
        });

    }
    private void validate(String username, String  userPassword){
        if((username.equals("abc")) && (userPassword.equals("1234"))){
            Intent intent= new Intent(MainActivity.this, MainActivity2.class);
            startActivity(intent);
        }
        else{
            Toast.makeText(getApplicationContext(), "invalid username/password. Try Again!!!", Toast.LENGTH_SHORT).show();
        }
    }
}