import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:hello_ai_os/ui/ar_camera_view.dart';

void main() {
  testWidgets('ARCameraView structure', (WidgetTester tester) async {
    await tester.pumpWidget(const MaterialApp(home: ARCameraView()));

    expect(find.byIcon(Icons.videocam_off), findsOneWidget);
    expect(find.text('Scan Space'), findsOneWidget);
    expect(find.byType(SpatialOverlay), findsOneWidget);
  });

  testWidgets('SpatialOverlay painting', (WidgetTester tester) async {
    await tester.pumpWidget(const MaterialApp(home: SpatialOverlay()));
    expect(find.byType(CustomPaint), findsOneWidget);
  });
}
