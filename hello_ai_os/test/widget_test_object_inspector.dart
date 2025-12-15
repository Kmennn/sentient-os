import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:hello_ai_os/ui/object_inspector_panel.dart';

void main() {
  testWidgets('Show Objects', (WidgetTester tester) async {
    final objects = [
      {
        "label": "Coffee Mug",
        "class_type": "vessel",
        "x": 0.1,
        "y": 0.2,
        "z": 0.0,
        "properties": {"is_fragile": true},
      },
    ];

    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(body: ObjectInspectorPanel(objects: objects)),
      ),
    );

    expect(find.text('Coffee Mug'), findsOneWidget);
    expect(find.text('vessel'), findsOneWidget);

    // Expand
    await tester.tap(find.text('Coffee Mug'));
    await tester.pumpAndSettle();

    expect(find.text('Fragile'), findsOneWidget);
  });
}
