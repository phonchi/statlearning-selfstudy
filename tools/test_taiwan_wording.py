import unittest
from check_taiwan_wording import check_words

class WordingContract(unittest.TestCase):
    def test_visible_and_feedback_use_house_terms(self):
        self.assertEqual(check_words('<p>配適</p><div data-fb="最大似然，靈敏度與閾值"></div>'),sorted(['配適','似然','靈敏度','閾值']))
        self.assertEqual(check_words('<p>擬合、最大概似、敏感度、門檻值</p>'),[])
    def test_source_code_and_saved_outputs_stay_verbatim(self):
        self.assertEqual(check_words('<div class="pseudo-code">配適</div><pre>閾值</pre><code>似然</code>'),[])
    def test_real_technical_terms_are_not_false_positives(self):
        self.assertEqual(check_words('<p>機率質量、水平線、正則化與正規化、演算法</p>'),[])
    def test_dynamic_messages_are_checked(self):
        self.assertEqual(check_words('<!-- PAGEJS:BEGIN --><script>const text = "重新配適";</script><!-- PAGEJS:END -->'),['配適'])
    def test_flashcard_payload_is_checked(self):
        self.assertEqual(check_words('<script>const FLASHCARDS = [{"front":"配適","back":"擬合"}];</script>'),['配適'])
if __name__=='__main__':unittest.main()
