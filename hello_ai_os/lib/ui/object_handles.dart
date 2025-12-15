import 'package:flutter/material.dart';

class ObjectHandles extends StatelessWidget {
  const ObjectHandles({super.key});

  @override
  Widget build(BuildContext context) {
    return Stack(
      children: [
        Positioned(
          top: 200,
          left: 150,
          child: GestureDetector(
            onTap: () {
              ScaffoldMessenger.of(
                context,
              ).showSnackBar(const SnackBar(content: Text("Object Selected")));
            },
            child: Container(
              width: 50,
              height: 50,
              decoration: BoxDecoration(
                color: Colors.white.withOpacity(0.3),
                shape: BoxShape.circle,
                border: Border.all(color: Colors.white),
              ),
              child: const Icon(Icons.touch_app, color: Colors.white),
            ),
          ),
        ),
      ],
    );
  }
}
