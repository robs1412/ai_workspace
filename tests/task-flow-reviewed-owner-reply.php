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

$domain=['status'=>'closed_with_proof','source_ref'=>'source@example.test','verification_readback'=>'Live event verified','packet_json'=>json_encode(['recovery_proof'=>['event_id'=>898]])];
if (!task_flow_preserves_reviewed_owner_reply($domain,$i,'owner_reply_pending_response')) throw new RuntimeException('Domain proof lost');
$domain['packet_json']=json_encode(['communication_proof'=>['requested_communication_verified'=>true,'source_ref'=>'source@example.test','sent_message_id'=>'sent@example.test','verified_recipients'=>['owner@example.test'],'requested_action'=>'Provide dates']]);
if (!task_flow_preserves_reviewed_owner_reply($domain,$i,'owner_reply_pending_response')) throw new RuntimeException('Communication proof lost');
$domain['packet_json']=json_encode(['recovery_proof'=>['message_id'=>'sent@example.test']]);
if (task_flow_preserves_reviewed_owner_reply($domain,$i,'owner_reply_pending_response')) throw new RuntimeException('Sent message treated as domain proof');
echo "3 business proof preservation checks passed\n";
