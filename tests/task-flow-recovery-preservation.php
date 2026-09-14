<?php
$source=file_get_contents('/Users/werkstatt/ai_workspace/scripts/task_flow_mysql_recorder.php');
$start=strpos($source,'function task_flow_preserves_recovery_assessment(');$end=strpos($source,'function task_flow_should_preserve_existing_packet(',$start);eval(substr($source,$start,$end-$start));
$e=['packet_json'=>json_encode(['recovery_assessment'=>['technical_blocker_reassessed'=>true]]),'verification_readback'=>'Activity381330 verified; follow-up remains','source_ref'=>'original'];
$weak=['status'=>'working','verification_readback'=>'still-pending','source_ref'=>'original'];
$cases=[
 [true,$e,$weak,'route_monitor'],
 [false,$e,array_merge($weak,['verification_readback'=>'Activity381400 newly verified']),'worker_result'],
 [false,$e,array_merge($weak,['source_ref'=>'new-reply']),'route_monitor'],
 [false,$e,$weak,'owner_instruction'],
 [false,$e,array_merge($weak,['reopened'=>true]),'route_monitor'],
 [false,array_merge($e,['packet_json'=>'{}']),$weak,'route_monitor'],
 [false,array_merge($e,['verification_readback'=>'']),$weak,'route_monitor'],
];
foreach($cases as [$want,$existing,$incoming,$event]) {if(task_flow_preserves_recovery_assessment($existing,$incoming,$event)!==$want)throw new RuntimeException('Recovery preservation mismatch');}
echo count($cases)," recovery preservation checks passed\n";
