 if self.stack.currentWidget() != self.question_page:
            return  # Sadece soru sayfasındayken işlem yap
        else:
            if sendData['detected'] == False:
                self.question_page.on_camera_choice(0)
            else:
                if sendData['row'] == 0 and sendData['col']==0:
                    print("A Şıkkı")
                    self.question_page.on_camera_choice(1)
                if sendData['row'] == 0 and sendData['col']==1:
                    print("B Şıkkı")
                    self.question_page.on_camera_choice(2)

                if sendData['row'] == 1 and sendData['col']==0:
                    print("C Şıkkı")
                    self.question_page.on_camera_choice(3)

                if sendData['row'] == 1 and sendData['col']==1:
                    print("D Şıkkı")
                    self.question_page.on_camera_choice(4)
      