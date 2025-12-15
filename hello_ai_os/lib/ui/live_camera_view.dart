import 'package:flutter/material.dart';

class LiveCameraView extends StatelessWidget {
  const LiveCameraView({super.key});

  @override
  Widget build(BuildContext context) {
    // In real app, this would use camera plugin Texture
    return Scaffold(
      backgroundColor: Colors.black,
      body: Center(
        child: Container(
          width: double.infinity,
          height: 300,
          color: Colors.grey[800],
          child: const Center(
            child: Icon(Icons.videocam, color: Colors.white, size: 50),
          ),
        ),
      ),
    );
  }
}
