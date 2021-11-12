package com.example.attendance01;

import androidx.annotation.NonNull;
import androidx.annotation.Nullable;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.app.ActivityCompat;
import androidx.core.content.ContextCompat;

import android.Manifest;
import android.annotation.SuppressLint;
import android.content.Context;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.graphics.Bitmap;
import android.location.Location;
import android.location.LocationManager;
import android.os.Bundle;
import android.os.Looper;
import android.provider.MediaStore;
import android.provider.Settings;
import android.view.View;
import android.widget.Button;
import android.widget.ImageView;
import android.widget.TextView;
import android.widget.Toast;

import com.google.android.gms.location.FusedLocationProviderClient;
import com.google.android.gms.location.LocationCallback;
import com.google.android.gms.location.LocationRequest;
import com.google.android.gms.location.LocationResult;
import com.google.android.gms.location.LocationServices;
import com.google.android.gms.tasks.OnCompleteListener;
import com.google.android.gms.tasks.Task;

public class MainActivity2 extends AppCompatActivity {

    Button btLocation;
    TextView tvLatitude,tvLongitude;
    FusedLocationProviderClient fusedLocationProviderClient;
    ImageView imageView;
    Button btOpen;
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main2);
        btLocation=findViewById(R.id.bt_location);
        tvLatitude=findViewById(R.id.tv_latitude);
        tvLongitude=findViewById(R.id.tv_longitude);
        fusedLocationProviderClient= LocationServices.getFusedLocationProviderClient(MainActivity2.this);

        btLocation.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                // check condition
                if (ActivityCompat.checkSelfPermission(MainActivity2.this,
                        Manifest.permission.ACCESS_FINE_LOCATION) == PackageManager.PERMISSION_GRANTED
                        && ActivityCompat.checkSelfPermission(MainActivity2.this,
                        Manifest.permission.ACCESS_COARSE_LOCATION )== PackageManager.PERMISSION_GRANTED) {
                    //when both permission granted
                    // call method
                    getCurrentLocation();


                }else{
                    //when permission is not granted
                    //request permission
                    ActivityCompat.requestPermissions(MainActivity2.this,new String[]{Manifest.permission.ACCESS_FINE_LOCATION
                                    ,Manifest.permission.ACCESS_FINE_LOCATION},
                            100);
                }
            }
        });

        //assign variables
        imageView=findViewById(R.id.image_view);
        btOpen=findViewById(R.id.bt_open);
        //request for camera permissions
        if(ContextCompat.checkSelfPermission(MainActivity2.this, Manifest.permission.CAMERA)!= PackageManager.PERMISSION_GRANTED){
            ActivityCompat.requestPermissions(MainActivity2.this,new String[]{Manifest.permission.CAMERA},100);
        }
        btOpen.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                //open camera
                Intent intent = new Intent(MediaStore.ACTION_IMAGE_CAPTURE);
                startActivityForResult(intent,100);
            }
        });
    }


    @SuppressLint("MissingSuperCall")
    @Override
    public void onRequestPermissionsResult(int requestCode, @NonNull String[] permissions, @NonNull int[] grantResults) {
        //check condition
        if(requestCode==100 && grantResults.length>0 &&(grantResults[0]+grantResults[1]
                ==PackageManager.PERMISSION_GRANTED)){
            //when permission granted
            //call method
            getCurrentLocation();

        }else{
            //when permission denied
            //display toast
            Toast.makeText(getApplicationContext(), "Permission denied", Toast.LENGTH_SHORT).show();
        }
    }

    @SuppressLint("MissingPermission")
    private void getCurrentLocation() {
        //initialize location manager
        LocationManager locationManager = (LocationManager) getSystemService(
                Context.LOCATION_SERVICE
        );

        // check condition
        if(locationManager.isProviderEnabled(LocationManager.GPS_PROVIDER)|| locationManager.isProviderEnabled(LocationManager.NETWORK_PROVIDER)){
            //when location service is enabled
            // get last location
            final Task<Location> locationTask = fusedLocationProviderClient.getLastLocation().addOnCompleteListener(new OnCompleteListener<Location>() {


                @Override
                public void onComplete(@NonNull Task<Location> task) {
                    // initialize location
                    Location location = task.getResult();
                    //check permission
                    if (location != null) {
                        //when location is not null then set latitude and longitude
                        tvLatitude.setText(String.valueOf(location.getLatitude()));
                        tvLongitude.setText(String.valueOf(location.getLongitude()));
                    } else {
                        //when location result is null initialise location request
                        LocationRequest locationRequest = new LocationRequest().setPriority(LocationRequest.PRIORITY_HIGH_ACCURACY)
                                .setInterval(10000)
                                .setFastestInterval(1000)
                                .setNumUpdates(1);

                        //initialize location call back
                        LocationCallback locationCallback = new LocationCallback() {
                            @Override
                            public void onLocationResult(LocationResult locationResult) {
                                // initialize location
                                Location location1 = locationResult.getLastLocation();
                                //set latitude
                                tvLatitude.setText(String.valueOf(location1.getLatitude()));
                                //set longitude
                                tvLongitude.setText(String.valueOf(location1.getLongitude()));
                            }
                        };
                        // request location update
                        fusedLocationProviderClient.requestLocationUpdates(locationRequest, locationCallback, Looper.myLooper());

                    }
                }
            });
        }else{
            // when location service is not enabled
            //open location settings
            startActivity(new Intent(Settings.ACTION_LOCATION_SOURCE_SETTINGS).setFlags(Intent.FLAG_ACTIVITY_NEW_TASK));
        }
    }


    @SuppressLint("MissingSuperCall")
    @Override
    protected void onActivityResult(int requestCode, int resultCode, @Nullable Intent data) {
        if(requestCode == 100){
            //get capture image
            Bitmap captureImage = (Bitmap) data.getExtras().get("data");
            //set capture image to imageview
            imageView.setImageBitmap(captureImage);
        }
    }
}