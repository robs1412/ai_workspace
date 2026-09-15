<?php
$source=file_get_contents(__DIR__.'/../scripts/task_flow_mysql_recorder.php');
$start=strpos($source,'function task_flow_preserves_reviewed_owner_reply(');
$end=strpos($source,'function task_flow_should_preserve_existing_packet(',$start);
eval(substr($source,$start,$end-$start));
$proof=['source_ref'=>'source@example.test','disposition'=>'acknowledgement_only','reviewed_at'=>'2026-09-15','source_excerpt'=>'Thank you'];
$e=['status'=>'filed_no_action','source_ref'=>'source@example.test','packet_json'=>json_encode(['owner_reply_resolution'=>$proof])];
$i=['status'=>'waiting','source_ref'=>'source@example.test'];
$cases=[
 [true,$e,$i,'owner_reply_pending_response'],
 [false,$e,$i,'owner_instruction'],
 [false,$e,array_merge($i,['reopened'=>true]),'owner_reply_pending_response'],
 [false,$e,array_merge($i,['source_ref'=>'new@example.test']),'owner_reply_pending_response'],
 [false,array_merge($e,['status'=>'working']),$i,'owner_reply_pending_response'],
 [false,array_merge($e,['packet_json'=>'{}']),$i,'owner_reply_pending_response'],
];
foreach($cases as [$want,$existing,$incoming,$event]) {
 if(task_flow_preserves_reviewed_owner_reply($existing,$incoming,$event)!==$want)throw new RuntimeException('Reviewed reply preservation mismatch');
}
echo count($cases)," reviewed owner reply preservation checks passed\n";
