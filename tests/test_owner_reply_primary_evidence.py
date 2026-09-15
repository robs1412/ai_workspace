import ast,json,unittest
from pathlib import Path

class PrimaryEvidenceTests(unittest.TestCase):
 def setUp(self):
  tree=ast.parse((Path(__file__).resolve().parents[1]/'scripts/ai_health_check.py').read_text())
  fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='owner_reply_primary_has_completion_evidence')
  ns={'json':json};exec(compile(ast.Module(body=[fn],type_ignores=[]),'health','exec'),ns);self.check=ns[fn.name]
 def row(self,status='closed_with_proof',proof=None,**extra):
  return {'status':status,'verification_readback':'Live event901 and sent confirmation verified','packet_json':json.dumps({'recovery_proof':proof if proof is not None else {'event_id':901},**extra})}
 def test_verified_domain_completion(self):self.assertTrue(self.check(self.row()))
 def test_reported_is_not_completion(self):self.assertFalse(self.check(self.row('reported')))
 def test_blocker_email_is_not_completion(self):self.assertFalse(self.check(self.row('blocked',{'message_id':'sent@test'})))
 def test_sent_message_alone_is_not_domain_proof(self):self.assertFalse(self.check(self.row(proof={'message_id':'sent@test'})))
 def test_generic_filing_is_not_completion(self):self.assertFalse(self.check(self.row('filed')))
 def test_owner_question_remains(self):self.assertFalse(self.check(self.row(owner_question_required=True)))
 def test_missing_structured_proof(self):self.assertFalse(self.check(self.row(proof={})))
 def test_malformed_packet(self):self.assertFalse(self.check({'status':'completed','packet_json':'oops'}))
 def test_source_reviewed_email_request(self):
  r=self.row(proof={});r['source_ref']='source@test';r['packet_json']=json.dumps({'communication_proof':{'requested_communication_verified':True,'source_ref':'source@test','sent_message_id':'sent@test','verified_recipients':['owner@test'],'requested_action':'Provide the available dates'}});self.assertTrue(self.check(r))
 def test_old_sent_email_cannot_cover_new_source(self):
  r=self.row(proof={});r['source_ref']='new@test';r['packet_json']=json.dumps({'communication_proof':{'requested_communication_verified':True,'source_ref':'old@test','sent_message_id':'sent@test','verified_recipients':['owner@test'],'requested_action':'Provide dates'}});self.assertFalse(self.check(r))
if __name__=='__main__':unittest.main()
