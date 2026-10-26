import copy
from datetime import date
import unittest
import pilot

class PublicationRules(unittest.TestCase):
    def setUp(self):
        self.p=pilot.load_data()['places'][0]
        self.day=date(2026,10,26)
    def test_expired_activity_leaves_current_section(self):
        self.assertEqual(len(pilot.active_events(self.p,date(2026,11,1))),1)
        self.assertEqual(pilot.active_events(self.p,date(2026,11,2)),[])
    def test_failed_and_changed_sources_suppress_old_card(self):
        for status in ('error','changed'):
            report={'sources':[{'url':u,'status':'unchanged'} for u in self.p['sources']]}
            report['sources'][0]['status']=status
            self.assertFalse(pilot.eligible(self.p,self.day,report))
    def test_fetch_does_not_refresh_stale_facts(self):
        report={'sources':[{'url':u,'status':'unchanged'} for u in self.p['sources']]}
        self.assertFalse(pilot.eligible(self.p,date(2026,11,27),report))
        self.assertTrue(pilot.eligible(self.p,self.day,report))
    def test_unknown_fee_is_not_free(self):
        p=copy.deepcopy(self.p);p['family_admission_jpy']=None
        self.assertIsNone(pilot.scores(p)[0])
        p['family_admission_jpy']=2800
        self.assertEqual(pilot.scores(p)[0],2)
    def test_new_fee_changes_score(self):
        p=copy.deepcopy(self.p)
        self.assertEqual(pilot.scores(p)[0],5)
        p['family_admission_jpy']=600
        self.assertEqual(pilot.scores(p)[0],4)
    def test_blocked_candidate_never_publishes(self):
        p=copy.deepcopy(self.p);p['status']='blocked'
        self.assertFalse(pilot.eligible(p,self.day,None))

if __name__=='__main__': unittest.main()
