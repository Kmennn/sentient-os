import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:hello_ai_os/ui/what_if_panel.dart';

void main() {
  testWidgets('WhatIfPanel triggers simulation', (WidgetTester tester) async {
    bool simulated = false;

    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(
          body: WhatIfPanel(onSimulate: (id, delta) => simulated = true),
        ),
      ),
    );

    await tester.tap(find.text("Simulate Change"));
    expect(simulated, isTrue);
  });

  testWidgets('WhatIfPanel displays result', (WidgetTester tester) async {
    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(
          body: WhatIfPanel(
            onSimulate: (_, __) {},
            simulationResult: "Load increases slightly.",
          ),
        ),
      ),
    );

    expect(find.text("Projected Impact:"), findsOneWidget);
    expect(find.text("Load increases slightly."), findsOneWidget);
  });
}
