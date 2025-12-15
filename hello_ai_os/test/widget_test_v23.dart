import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:hello_ai_os/ui/live_camera_view.dart';
import 'package:hello_ai_os/ui/depth_overlay.dart';
import 'package:hello_ai_os/ui/manipulation_preview.dart';

void main() {
  testWidgets('LiveCameraView placeholder', (WidgetTester tester) async {
    await tester.pumpWidget(const MaterialApp(home: LiveCameraView()));
    expect(find.byIcon(Icons.videocam), findsOneWidget);
  });

  testWidgets('DepthOverlay gradient', (WidgetTester tester) async {
    await tester.pumpWidget(const MaterialApp(home: DepthOverlay()));
    expect(find.text('Depth Estimation: ON'), findsOneWidget);
  });

  testWidgets('ManipulationPreview status', (WidgetTester tester) async {
    await tester.pumpWidget(
      const MaterialApp(
        home: Scaffold(body: Stack(children: [ManipulationPreview()])),
      ),
    );
    expect(find.text('Planning: Click at (100, 200)'), findsOneWidget);
  });
}
