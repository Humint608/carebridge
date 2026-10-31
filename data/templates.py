# -*- coding: utf-8 -*-
"""
CareBridge 합성 관찰메모 템플릿 (5개 언어)
- 모든 문장은 학습용으로 직접 작성한 합성(가상) 문장이며 실제 수급자 기록이 아님
- 언어: ko(한국어), vi(베트남어), ne(네팔어), id(인도네시아어), uz(우즈베크어)
- 클래스(기록 항목): VISIT, SUPPORT, MEAL, SLEEP, DISCOMFORT, MEDICATION, EXCRETION, MOOD, EVENT
- {s}=대상자 호칭, {t}=식사 시점, {p}=신체 부위, {h}=시각
"""

LANGS = ["ko", "vi", "ne", "id", "uz"]

SUBJ = {
    "ko": ["어르신은", "어르신께서", "할머니께서", "할아버지께서", ""],
    "vi": ["Bà", "Ông", "Cụ", "Bà cụ"],
    "ne": ["हजुरआमाले", "हजुरबुबाले", "उहाँले"],
    "id": ["Nenek", "Kakek", "Ibu", "Beliau", "Oma"],
    "uz": ["Buvi", "Bobo", "Buvijon", "Bobojon", "Onaxon"],
}
# 주어 없는(주격조사 없는) 형태 — 수면/정서 등 자동사 문장용
SUBJ_PLAIN = {
    "ko": ["어르신은", "할머니는", "할아버지는", ""],
    "vi": ["Bà", "Ông", "Cụ"],
    "ne": ["हजुरआमा", "हजुरबुबा", "उहाँ"],
    "id": ["Nenek", "Kakek", "Ibu", "Oma"],
    "uz": ["Buvi", "Bobo", "Buvijon", "Onaxon"],
}

MEAL_TIME = {
    "ko": {"BREAKFAST": ["아침을", "아침 식사를"], "LUNCH": ["점심을", "점심 식사를"], "DINNER": ["저녁을", "저녁 식사를"], "SNACK": ["간식을"], "UNSPEC": ["식사를", "밥을", "진지를"]},
    "vi": {"BREAKFAST": ["bữa sáng"], "LUNCH": ["bữa trưa", "cơm trưa"], "DINNER": ["bữa tối", "cơm tối"], "SNACK": ["đồ ăn nhẹ", "bánh"], "UNSPEC": ["cơm", "bữa ăn"]},
    "ne": {"BREAKFAST": ["बिहानको खाना", "नास्ता"], "LUNCH": ["दिउँसोको खाना"], "DINNER": ["बेलुकाको खाना", "रातिको खाना"], "SNACK": ["खाजा"], "UNSPEC": ["खाना", "भात"]},
    "id": {"BREAKFAST": ["sarapan"], "LUNCH": ["makan siang"], "DINNER": ["makan malam"], "SNACK": ["camilan", "kue"], "UNSPEC": ["makanan", "nasi"]},
    "uz": {"BREAKFAST": ["nonushta"], "LUNCH": ["tushlik"], "DINNER": ["kechki ovqat"], "SNACK": ["yengil tamaddi", "pechene"], "UNSPEC": ["ovqat", "taom"]},
}

MEAL_AMT = {
    "ko": {
        "ALL": ["{s} {t} 다 드셨습니다", "{s} {t} 전부 드셨어요", "{s} {t} 남김없이 드셨습니다"],
        "MOST": ["{s} {t} 거의 다 드셨습니다", "{s} {t} 대부분 드셨어요", "{s} {t} 조금 남기고 드셨습니다"],
        "HALF": ["{s} {t} 절반 드셨습니다", "{s} {t} 반 정도 드셨어요", "{s} {t} 반쯤 드셨습니다"],
        "LITTLE": ["{s} {t} 조금 드셨습니다", "{s} {t} 몇 숟가락만 드셨어요", "{s} {t} 아주 조금만 드셨습니다"],
        "NONE": ["{s} {t} 안 드셨습니다", "{s} {t} 드시지 않으셨어요", "{s} {t} 거부하셨습니다"],
        "UNSPEC": ["{s} {t} 드셨습니다", "{s} {t} 드셨어요", "{s} {t} 하셨습니다"],
    },
    "vi": {
        "ALL": ["{s} ăn hết {t}", "{s} đã ăn hết sạch {t}", "{s} ăn sạch {t}"],
        "MOST": ["{s} ăn gần hết {t}", "{s} ăn gần hết phần {t}", "{s} ăn hầu hết {t}"],
        "HALF": ["{s} ăn được một nửa {t}", "{s} ăn khoảng một nửa {t}", "{s} chỉ ăn nửa phần {t}"],
        "LITTLE": ["{s} chỉ ăn một chút {t}", "{s} ăn một ít {t}", "{s} ăn được vài thìa {t}"],
        "NONE": ["{s} không ăn {t}", "{s} bỏ {t}", "{s} không chịu ăn {t}"],
        "UNSPEC": ["{s} đã ăn {t}", "{s} có ăn {t}", "{s} ăn {t} rồi"],
    },
    "ne": {
        "ALL": ["{s} {t} सबै खानुभयो", "{s} {t} पूरै खानुभयो", "{s} {t} सक्नुभयो"],
        "MOST": ["{s} {t} लगभग सबै खानुभयो", "{s} {t} धेरैजसो खानुभयो", "{s} {t} अलिकति मात्र छोड्नुभयो"],
        "HALF": ["{s} {t} आधा खानुभयो", "{s} {t} आधा जति खानुभयो", "{s} {t} आधा मात्र खानुभयो"],
        "LITTLE": ["{s} {t} थोरै मात्र खानुभयो", "{s} {t} अलिकति खानुभयो", "{s} {t} दुई तीन चम्चा मात्र खानुभयो"],
        "NONE": ["{s} {t} खानुभएन", "{s} {t} खान मान्नुभएन", "{s} {t} छुनुभएन"],
        "UNSPEC": ["{s} {t} खानुभयो", "{s} {t} खाइसक्नुभयो", "{s} {t} लिनुभयो"],
    },
    "id": {
        "ALL": ["{s} menghabiskan {t}", "{s} makan {t} sampai habis", "{t} {s} habis semua"],
        "MOST": ["{s} makan hampir semua {t}", "{s} hampir menghabiskan {t}", "{s} makan sebagian besar {t}"],
        "HALF": ["{s} makan setengah porsi {t}", "{s} hanya makan separuh {t}", "{s} makan kira-kira setengah {t}"],
        "LITTLE": ["{s} hanya makan sedikit {t}", "{s} makan {t} sedikit saja", "{s} cuma makan beberapa sendok {t}"],
        "NONE": ["{s} tidak mau makan {t}", "{s} menolak {t}", "{s} tidak makan {t} sama sekali"],
        "UNSPEC": ["{s} sudah makan {t}", "{s} makan {t}", "{s} sudah {t}"],
    },
    "uz": {
        "ALL": ["{s} {t}ni to'liq yedi", "{s} {t}ni hammasini yedi", "{s} {t}ni oxirigacha yedi"],
        "MOST": ["{s} {t}ning deyarli hammasini yedi", "{s} {t}ning ko'p qismini yedi", "{s} {t}dan ozgina qoldirdi"],
        "HALF": ["{s} {t}ning yarmini yedi", "{s} {t}ni yarim porsiya yedi", "{s} {t}ning yarmiga yaqinini yedi"],
        "LITTLE": ["{s} {t}dan ozgina yedi", "{s} {t}dan bir-ikki qoshiq yedi", "{s} {t}dan juda kam yedi"],
        "NONE": ["{s} {t} yemadi", "{s} {t}dan bosh tortdi", "{s} {t}ga qo'l urmadi"],
        "UNSPEC": ["{s} {t} yedi", "{s} {t}ni yedi", "{s} {t} qildi"],
    },
}

MED = {
    "ko": {
        "TAKEN": ["{s} 약을 드셨습니다", "약 복용을 확인했습니다", "{s} 아침 약을 드시는 것을 봤습니다"],
        "NOT_CONFIRMED": ["복약 여부는 확인하지 못했습니다", "약을 드셨는지 확인 못 했습니다", "약 드신 것은 확인이 안 됐습니다"],
        "REFUSED": ["{s} 약을 안 드시겠다고 하셨습니다", "{s} 약 드시기를 거부하셨습니다", "{s} 약을 뱉으셨습니다"],
    },
    "vi": {
        "TAKEN": ["{s} đã uống thuốc", "Tôi thấy {s} uống thuốc rồi", "{s} uống thuốc đầy đủ"],
        "NOT_CONFIRMED": ["Tôi chưa kiểm tra được {s} đã uống thuốc chưa", "Không xác nhận được việc uống thuốc", "Chưa rõ {s} uống thuốc hay chưa"],
        "REFUSED": ["{s} không chịu uống thuốc", "{s} từ chối uống thuốc", "{s} nhổ thuốc ra"],
    },
    "ne": {
        "TAKEN": ["{s} औषधि खानुभयो", "औषधि खाएको देखेँ", "{s} समयमै औषधि खानुभयो"],
        "NOT_CONFIRMED": ["औषधि खानुभयो कि भएन जाँच गर्न सकिनँ", "औषधि खाएको पक्का भएन", "औषधिबारे थाहा पाउन सकिनँ"],
        "REFUSED": ["{s} औषधि खान मान्नुभएन", "{s} औषधि खान अस्वीकार गर्नुभयो", "{s} औषधि थुकिदिनुभयो"],
    },
    "id": {
        "TAKEN": ["{s} sudah minum obat", "Saya lihat {s} minum obat", "{s} minum obat tepat waktu"],
        "NOT_CONFIRMED": ["Saya belum sempat memastikan obatnya sudah diminum", "Belum dicek apakah obat sudah diminum", "Tidak tahu {s} sudah minum obat atau belum"],
        "REFUSED": ["{s} menolak minum obat", "{s} tidak mau minum obat", "{s} memuntahkan obatnya"],
    },
    "uz": {
        "TAKEN": ["{s} dorisini ichdi", "Dori ichganini ko'rdim", "{s} dorini vaqtida ichdi"],
        "NOT_CONFIRMED": ["Dori ichganini tekshira olmadim", "Dori ichilgani aniq emas", "{s} dori ichdimi yo'qmi bilmadim"],
        "REFUSED": ["{s} dori ichishdan bosh tortdi", "{s} dorini ichmayman dedi", "{s} dorini tupurib tashladi"],
    },
}

SLEEP = {
    "ko": {
        "GOOD": ["{s} 밤에 잘 주무셨습니다", "{s} 푹 주무셨다고 하셨어요", "{s} 낮잠을 편하게 주무셨습니다"],
        "POOR": ["{s} 잠을 잘 못 주무셨습니다", "{s} 밤에 잠을 설치셨어요", "{s} 잠이 안 온다고 하셨습니다"],
        "WOKE": ["{s} 밤에 여러 번 깨셨습니다", "{s} 새벽에 자주 깨셨어요", "{s} 자다가 몇 번 일어나셨습니다"],
    },
    "vi": {
        "GOOD": ["Đêm qua {s} ngủ ngon", "{s} ngủ rất say", "{s} ngủ trưa ngon giấc"],
        "POOR": ["{s} ngủ không ngon", "{s} bị mất ngủ", "{s} khó ngủ cả đêm"],
        "WOKE": ["{s} thức dậy nhiều lần trong đêm", "{s} hay tỉnh giấc lúc nửa đêm", "{s} tỉnh dậy mấy lần"],
    },
    "ne": {
        "GOOD": ["{s} राति राम्ररी सुत्नुभयो", "{s} मस्त निदाउनुभयो", "{s} दिउँसो आरामसँग सुत्नुभयो"],
        "POOR": ["{s} राति राम्रोसँग निदाउन सक्नुभएन", "{s} लाई निद्रा लागेन", "{s} रातभर छटपट गर्दै सुत्नुभयो"],
        "WOKE": ["{s} राति धेरै पटक ब्यूँझनुभयो", "{s} मध्यरातमा बारम्बार उठ्नुभयो", "{s} दुई तीन पटक ब्यूँझनुभयो"],
    },
    "id": {
        "GOOD": ["{s} tidur nyenyak semalam", "{s} tidur pulas", "{s} tidur siang dengan tenang"],
        "POOR": ["{s} susah tidur", "Tidur {s} kurang nyenyak", "{s} tidak bisa tidur semalaman"],
        "WOKE": ["{s} sering terbangun malam hari", "{s} bangun beberapa kali tengah malam", "{s} terbangun berkali-kali"],
    },
    "uz": {
        "GOOD": ["{s} kechasi yaxshi uxladi", "{s} tinch uxladi", "{s} tushlikdan keyin yaxshi dam olib uxladi"],
        "POOR": ["{s} yaxshi uxlay olmadi", "{s}ning uyqusi yomon bo'ldi", "{s} tun bo'yi uxlamadi"],
        "WOKE": ["{s} kechasi bir necha marta uyg'ondi", "{s} yarim tunda tez-tez uyg'ondi", "{s} ikki-uch marta uyg'onib ketdi"],
    },
}

BODY = {
    "ko": {"KNEE": ["무릎이"], "BACK": ["허리가"], "HEAD": ["머리가"], "STOMACH": ["배가"], "LEG": ["다리가"], "SHOULDER": ["어깨가"], "CHEST": ["가슴이"], "UNSPEC": ["몸이", "여기저기가"]},
    "vi": {"KNEE": ["đầu gối"], "BACK": ["lưng"], "HEAD": ["đầu"], "STOMACH": ["bụng"], "LEG": ["chân"], "SHOULDER": ["vai"], "CHEST": ["ngực"], "UNSPEC": ["người", "toàn thân"]},
    "ne": {"KNEE": ["घुँडा"], "BACK": ["ढाड", "कम्मर"], "HEAD": ["टाउको"], "STOMACH": ["पेट"], "LEG": ["खुट्टा"], "SHOULDER": ["काँध"], "CHEST": ["छाती"], "UNSPEC": ["जिउ", "शरीर"]},
    "id": {"KNEE": ["lutut"], "BACK": ["punggung", "pinggang"], "HEAD": ["kepala"], "STOMACH": ["perut"], "LEG": ["kaki"], "SHOULDER": ["bahu"], "CHEST": ["dada"], "UNSPEC": ["badan", "seluruh badan"]},
    "uz": {"KNEE": ["tizzasi"], "BACK": ["beli"], "HEAD": ["boshi"], "STOMACH": ["qorni"], "LEG": ["oyog'i"], "SHOULDER": ["yelkasi"], "CHEST": ["ko'kragi"], "UNSPEC": ["badani", "hamma yeri"]},
}
DISCOMFORT_T = {
    "ko": ["{s} {p} 불편하다고 말씀하셨습니다", "{p} 아프다고 하셨어요", "{s} {p} 쑤신다고 하셨습니다", "{p} 결린다고 말씀하셨어요"],
    "vi": ["{s} nói bị đau {p}", "{s} kêu {p} khó chịu", "{s} than đau {p}", "{s} bảo {p} nhức"],
    "ne": ["{s} {p} दुख्यो भन्नुभयो", "{s} {p} असजिलो भएको बताउनुभयो", "{s} {p} कटकटी खान्छ भन्नुभयो", "{p} दुखेको गुनासो गर्नुभयो"],
    "id": ["{s} bilang {p} sakit", "{s} mengeluh sakit {p}", "{s} merasa {p} tidak enak", "{s} mengeluh {p} pegal"],
    "uz": ["{s} {p} og'riyotganini aytdi", "{s} {p} og'riyapti dedi", "{s} {p} bezovta qilayotganini aytdi", "{s} {p} sanchiyapti deb shikoyat qildi"],
}

SUPPORT = {
    "ko": {
        "BATH": ["목욕을 도와드렸습니다", "세면을 도와드렸어요", "머리를 감겨 드렸습니다"],
        "WALK": ["산책을 함께 했습니다", "휠체어 이동을 도와드렸습니다", "화장실까지 부축해 드렸어요"],
        "DRESS": ["옷 갈아입는 것을 도와드렸습니다", "환복을 도와드렸어요", "양말을 신겨 드렸습니다"],
        "MEAL_ASSIST": ["식사를 떠먹여 드렸습니다", "식사 보조를 했습니다", "반찬을 잘게 잘라 드렸어요"],
        "CLEAN": ["방 청소를 했습니다", "침구를 정리했습니다", "빨래를 해 드렸어요"],
        "REPOSITION": ["두 시간마다 자세를 바꿔 드렸습니다", "체위 변경을 해 드렸습니다", "몸을 옆으로 돌려 눕혀 드렸어요"],
    },
    "vi": {
        "BATH": ["Tôi giúp {s} tắm", "Tôi lau người cho {s}", "Tôi gội đầu cho {s}"],
        "WALK": ["Tôi dìu {s} đi dạo", "Tôi giúp {s} di chuyển bằng xe lăn", "Tôi đỡ {s} đi vệ sinh"],
        "DRESS": ["Tôi giúp {s} thay quần áo", "Tôi mặc áo cho {s}", "Tôi đi tất cho {s}"],
        "MEAL_ASSIST": ["Tôi đút cho {s} ăn", "Tôi hỗ trợ {s} ăn", "Tôi cắt nhỏ thức ăn cho {s}"],
        "CLEAN": ["Tôi dọn dẹp phòng", "Tôi thay ga giường", "Tôi giặt quần áo cho {s}"],
        "REPOSITION": ["Tôi giúp {s} trở mình", "Cứ hai tiếng tôi đổi tư thế cho {s}", "Tôi xoay người cho {s} nằm nghiêng"],
    },
    "ne": {
        "BATH": ["{s2}लाई नुहाउन सहयोग गरेँ", "{s2}को जिउ पुछिदिएँ", "{s2}को कपाल धोइदिएँ"],
        "WALK": ["{s2}सँग हिँड्न गएँ", "{s2}लाई ह्वीलचेयरमा सार्न सहयोग गरेँ", "{s2}लाई शौचालयसम्म समातेर लगेँ"],
        "DRESS": ["{s2}लाई लुगा फेर्न सहयोग गरेँ", "{s2}लाई लुगा लगाइदिएँ", "{s2}लाई मोजा लगाइदिएँ"],
        "MEAL_ASSIST": ["{s2}लाई खाना खुवाइदिएँ", "{s2}लाई खाना खान सहयोग गरेँ", "{s2}को खाना सानो सानो टुक्रा पारिदिएँ"],
        "CLEAN": ["कोठा सफा गरेँ", "ओछ्यान मिलाएँ", "{s2}का लुगा धोइदिएँ"],
        "REPOSITION": ["{s2}लाई कोल्टे फेर्न सहयोग गरेँ", "हरेक दुई घण्टामा सुताइ फेरिदिएँ", "{s2}लाई छेउतिर फर्काएर सुताइदिएँ"],
    },
    "id": {
        "BATH": ["Saya membantu {s} mandi", "Saya menyeka badan {s}", "Saya mencuci rambut {s}"],
        "WALK": ["Saya menemani {s} jalan-jalan", "Saya membantu {s} pindah ke kursi roda", "Saya memapah {s} ke kamar mandi"],
        "DRESS": ["Saya membantu {s} ganti baju", "Saya memakaikan baju {s}", "Saya memakaikan kaus kaki {s}"],
        "MEAL_ASSIST": ["Saya menyuapi {s}", "Saya membantu {s} makan", "Saya memotong kecil-kecil makanan {s}"],
        "CLEAN": ["Saya membersihkan kamar", "Saya merapikan tempat tidur", "Saya mencuci pakaian {s}"],
        "REPOSITION": ["Saya membantu mengubah posisi tidur {s}", "Setiap dua jam saya ubah posisi {s}", "Saya memiringkan badan {s}"],
    },
    "uz": {
        "BATH": ["{s3}ni cho'miltirdim", "{s3}ga yuvinishda yordam berdim", "{s3}ning sochini yuvdim"],
        "WALK": ["{s3} bilan sayr qildik", "{s3}ni aravachaga o'tkazishga yordam berdim", "{s3}ni hojatxonagacha suyab bordim"],
        "DRESS": ["{s3}ga kiyim almashtirishda yordam berdim", "{s3}ga ko'ylak kiydirdim", "{s3}ga paypoq kiydirdim"],
        "MEAL_ASSIST": ["{s3}ga ovqat yedirdim", "{s3}ga ovqatlanishda yordam berdim", "{s3}ning ovqatini mayda qilib to'g'radim"],
        "CLEAN": ["Xonani tozaladim", "Yotoqni yig'ishtirdim", "{s3}ning kiyimlarini yuvdim"],
        "REPOSITION": ["{s3}ning yotish holatini o'zgartirdim", "Har ikki soatda {s3}ni ag'dardim", "{s3}ni yonboshiga yotqizdim"],
    },
}
OBJ = {  # 목적어/소유격용 호칭
    "ko": ["어르신"], "vi": ["bà", "ông", "cụ"], "ne": ["हजुरआमा", "हजुरबुबा"],
    "id": ["Nenek", "Kakek", "Ibu", "Oma"], "uz": ["Buvi", "Bobo", "Buvijon"],
}

MOOD = {
    "ko": {
        "GOOD": ["{s} 기분이 좋아 보이셨습니다", "{s} 웃으면서 이야기하셨어요", "{s} 노래를 따라 부르셨습니다"],
        "LOW": ["{s} 기운이 없어 보이셨습니다", "{s} 우울하다고 말씀하셨어요", "{s} 말씀이 평소보다 적으셨습니다"],
        "AGITATED": ["{s} 화를 내셨습니다", "{s} 불안해하셨어요", "{s} 가족을 찾으며 초조해하셨습니다"],
    },
    "vi": {
        "GOOD": ["{s} vui vẻ nói chuyện nhiều", "{s} cười rất tươi", "{s} hát theo đài"],
        "LOW": ["{s} có vẻ buồn", "{s} ít nói hơn mọi ngày", "{s} trông mệt mỏi chán nản"],
        "AGITATED": ["{s} cáu gắt", "{s} lo lắng đòi gặp con", "{s} bồn chồn không yên"],
    },
    "ne": {
        "GOOD": ["{s} खुसी देखिनुभयो", "{s} हाँसेर कुरा गर्नुभयो", "{s} गीत गाउनुभयो"],
        "LOW": ["{s} उदास देखिनुभयो", "{s} सधैंभन्दा कम बोल्नुभयो", "{s} थकित र निराश देखिनुभयो"],
        "AGITATED": ["{s} रिसाउनुभयो", "{s} छोराछोरी खोज्दै छटपटाउनुभयो", "{s} बेचैन हुनुभयो"],
    },
    "id": {
        "GOOD": ["{s} terlihat senang", "{s} banyak tersenyum dan mengobrol", "{s} ikut bernyanyi"],
        "LOW": ["{s} terlihat sedih", "{s} lebih pendiam dari biasanya", "{s} tampak lesu dan murung"],
        "AGITATED": ["{s} marah-marah", "{s} gelisah mencari anaknya", "{s} tampak cemas terus"],
    },
    "uz": {
        "GOOD": ["{s}ning kayfiyati yaxshi edi", "{s} kulib gaplashdi", "{s} qo'shiq aytdi"],
        "LOW": ["{s} xafa ko'rindi", "{s} odatdagidan kam gapirdi", "{s} holsiz va tushkun ko'rindi"],
        "AGITATED": ["{s}ning jahli chiqdi", "{s} bezovtalanib bolalarini so'radi", "{s} juda xavotirlandi"],
    },
}

EXCR = {
    "ko": {
        "NORMAL": ["{s} 대변을 보셨습니다", "{s} 화장실에 다녀오셨어요", "{s} 소변을 잘 보셨습니다"],
        "NONE": ["{s} 오늘 대변을 보지 않으셨습니다", "{s} 사흘째 변을 못 보셨어요", "{s} 소변을 거의 안 보셨습니다"],
        "LOOSE": ["{s} 묽은 변을 보셨습니다", "{s} 설사를 하셨어요", "{s} 변이 물처럼 나왔습니다"],
    },
    "vi": {
        "NORMAL": ["{s} đã đi đại tiện", "{s} đi vệ sinh bình thường", "{s} đi tiểu bình thường"],
        "NONE": ["Hôm nay {s} chưa đi đại tiện", "{s} ba ngày chưa đi ngoài", "{s} đi tiểu rất ít"],
        "LOOSE": ["{s} đi ngoài phân lỏng", "{s} bị tiêu chảy", "{s} đi ngoài ra nước"],
    },
    "ne": {
        "NORMAL": ["{s2} दिसा गर्नुभयो", "{s2} शौचालय जानुभयो", "{s2} पिसाब सामान्य गर्नुभयो"],
        "NONE": ["आज {s2} दिसा गर्नुभएन", "{s2} तीन दिनदेखि दिसा गर्नुभएको छैन", "{s2} पिसाब निकै कम गर्नुभयो"],
        "LOOSE": ["{s2} पातलो दिसा गर्नुभयो", "{s2} लाई पखाला लाग्यो", "{s2} पानीजस्तो दिसा गर्नुभयो"],
    },
    "id": {
        "NORMAL": ["{s} sudah buang air besar", "{s} BAB normal", "{s} buang air kecil lancar"],
        "NONE": ["{s} belum buang air besar hari ini", "{s} sudah tiga hari tidak BAB", "{s} jarang buang air kecil"],
        "LOOSE": ["{s} BAB cair", "{s} diare", "{s} buang air besar encer"],
    },
    "uz": {
        "NORMAL": ["{s} hojatxonaga bordi", "{s}ning ichi normal keldi", "{s} siydik normal chiqardi"],
        "NONE": ["Bugun {s}ning ichi kelmadi", "{s}ning uch kundan beri ichi kelmayapti", "{s} juda kam siydi"],
        "LOOSE": ["{s}ning ichi suyuq keldi", "{s}ning ichi ketdi", "{s}ning ichi suvday keldi"],
    },
}

EVENT = {
    "ko": {
        "FALL": ["{s} 넘어지셨습니다", "{s} 침대에서 떨어지셨어요", "{s} 화장실에서 미끄러져 넘어지셨습니다"],
        "NEAR_FALL": ["{s} 넘어질 뻔하셨습니다", "{s} 일어나다 휘청하셨어요", "{s} 미끄러질 뻔하셨습니다"],
    },
    "vi": {
        "FALL": ["{s} bị ngã", "{s} ngã khỏi giường", "{s} trượt chân ngã trong nhà tắm"],
        "NEAR_FALL": ["{s} suýt ngã", "{s} đứng dậy bị loạng choạng", "{s} suýt trượt chân"],
    },
    "ne": {
        "FALL": ["{s2} लड्नुभयो", "{s2} खाटबाट खस्नुभयो", "{s2} बाथरुममा चिप्लिएर लड्नुभयो"],
        "NEAR_FALL": ["{s2} लड्न लाग्नुभयो", "{s2} उठ्दा लरखराउनुभयो", "{s2} चिप्लिन लाग्नुभयो"],
    },
    "id": {
        "FALL": ["{s} jatuh", "{s} jatuh dari tempat tidur", "{s} terpeleset dan jatuh di kamar mandi"],
        "NEAR_FALL": ["{s} hampir jatuh", "{s} sempoyongan waktu berdiri", "{s} hampir terpeleset"],
    },
    "uz": {
        "FALL": ["{s} yiqilib tushdi", "{s} karavotdan yiqildi", "{s} hammomda sirpanib yiqildi"],
        "NEAR_FALL": ["{s} yiqilib tushishiga oz qoldi", "{s} o'rnidan turganda gandiraklab ketdi", "{s} sirpanib ketishiga sal qoldi"],
    },
}

VISIT = {
    "ko": ["{h}에 방문했습니다", "{h} 방문", "{h}에 댁에 도착했어요", "방문 시간은 {h}입니다"],
    "vi": ["Tôi đến nhà lúc {h}", "Đến lúc {h}", "Tôi bắt đầu ca lúc {h}", "Thời gian thăm {h}"],
    "ne": ["{h} बजे पुगेँ", "{h} बजे घर पुगेँ", "भेटघाट समय {h} बजे", "{h} बजे काम सुरु गरेँ"],
    "id": ["Saya datang jam {h}", "Tiba pukul {h}", "Kunjungan jam {h}", "Saya mulai kerja pukul {h}"],
    "uz": ["Soat {h} da keldim", "Soat {h} da yetib keldim", "Tashrif vaqti soat {h}", "Soat {h} da ishni boshladim"],
}

JOINERS = {
    "ko": [". ", ". ", ", ", "\n"],
    "vi": [". ", ". ", ", ", " và ", "\n"],
    "ne": ["। ", ". ", ", ", " र ", "\n"],
    "id": [". ", ". ", ", ", " dan ", "\n"],
    "uz": [". ", ". ", ", ", " va ", "\n"],
}

# ---------------------------------------------------------------------------
# 핵심 표현(anchor) 사전: 문형과 무관하게 세부값을 결정하는 짧은 표현.
# 문장 틀이 달라도 핵심어로 판단하도록 학습 데이터에 단독/호칭 결합 형태로 추가한다.
# ---------------------------------------------------------------------------
ANCHOR = {
    "MEAL": {
        "ko": {"ALL": ["다 드심", "전부 드심", "한 그릇 다 비우심"], "MOST": ["거의 다 드심", "대부분 드심"], "HALF": ["절반 드심", "반 정도 드심", "반 그릇 드심"], "LITTLE": ["조금 드심", "몇 숟가락 드심", "조금만 드심"], "NONE": ["안 드심", "안 드시겠다고 하심", "식사 거부"], "UNSPEC": ["식사하심", "드심"]},
        "vi": {"ALL": ["ăn hết", "ăn hết sạch"], "MOST": ["ăn gần hết"], "HALF": ["ăn một nửa", "ăn nửa bát"], "LITTLE": ["ăn một chút", "ăn vài thìa", "ăn ít"], "NONE": ["không ăn", "không chịu ăn", "bỏ bữa"], "UNSPEC": ["đã ăn", "ăn rồi"]},
        "ne": {"ALL": ["सबै खानुभयो", "पूरै खानुभयो"], "MOST": ["लगभग सबै खानुभयो"], "HALF": ["आधा खानुभयो"], "LITTLE": ["थोरै खानुभयो", "अलिकति मात्र खानुभयो"], "NONE": ["खानुभएन", "खान मान्नुभएन"], "UNSPEC": ["खाना खानुभयो"]},
        "id": {"ALL": ["habis", "menghabiskan makanan"], "MOST": ["hampir habis"], "HALF": ["setengah porsi", "separuh"], "LITTLE": ["sedikit saja", "beberapa sendok", "makan sedikit"], "NONE": ["tidak mau makan", "menolak makan"], "UNSPEC": ["sudah makan"]},
        "uz": {"ALL": ["hammasini yedi", "to'liq yedi"], "MOST": ["deyarli hammasini yedi"], "HALF": ["yarmini yedi"], "LITTLE": ["ozgina yedi", "bir-ikki qoshiq yedi"], "NONE": ["yemadi", "ovqatdan bosh tortdi"], "UNSPEC": ["ovqat yedi"]},
    },
    "MEDICATION": {
        "ko": {"TAKEN": ["약 드심", "약 드시는 것 확인", "약 복용함", "약은 드셨습니다"], "NOT_CONFIRMED": ["약 확인 못 함", "복약 미확인", "약 드셨는지 모름"], "REFUSED": ["약 거부", "약 안 드신다고 하심", "약 안 드심"]},
        "vi": {"TAKEN": ["đã uống thuốc", "uống thuốc rồi"], "NOT_CONFIRMED": ["chưa kiểm tra thuốc", "không biết đã uống thuốc chưa"], "REFUSED": ["không chịu uống thuốc", "từ chối uống thuốc"]},
        "ne": {"TAKEN": ["औषधि खानुभयो"], "NOT_CONFIRMED": ["औषधि जाँच गर्न सकिनँ", "औषधि थाहा भएन"], "REFUSED": ["औषधि खान मान्नुभएन"]},
        "id": {"TAKEN": ["sudah minum obat"], "NOT_CONFIRMED": ["belum cek obat", "tidak tahu sudah minum obat"], "REFUSED": ["tidak mau minum obat", "menolak obat"]},
        "uz": {"TAKEN": ["dori ichdi", "dorini ichdi"], "NOT_CONFIRMED": ["dorini tekshirmadim", "dori ichganini bilmadim"], "REFUSED": ["dori ichmadi", "dori ichishni xohlamadi"]},
    },
    "SLEEP": {
        "ko": {"GOOD": ["잘 주무심", "푹 주무심", "잘 잤다고 하심"], "POOR": ["잠 못 주무심", "잠을 통 못 잤다고 하심", "못 잤다고 하심", "불면"], "WOKE": ["자주 깨심", "여러 번 깨심", "밤에 깨심"]},
        "vi": {"GOOD": ["ngủ ngon", "ngủ say"], "POOR": ["ngủ không ngon", "mất ngủ", "khó ngủ"], "WOKE": ["thức dậy nhiều lần", "hay tỉnh giấc", "tỉnh dậy mấy lần"]},
        "ne": {"GOOD": ["राम्ररी सुत्नुभयो"], "POOR": ["निद्रा लागेन", "निदाउन सक्नुभएन"], "WOKE": ["धेरै पटक ब्यूँझनुभयो"]},
        "id": {"GOOD": ["tidur nyenyak", "tidur pulas", "tidurnya nyenyak"], "POOR": ["susah tidur", "kurang tidur", "tidak bisa tidur"], "WOKE": ["sering terbangun", "bangun berkali-kali"]},
        "uz": {"GOOD": ["yaxshi uxladi", "tinch uxladi"], "POOR": ["yaxshi uxlay olmadi", "uxlamadi", "uyqusi yomon"], "WOKE": ["tez-tez uyg'ondi", "bir necha marta uyg'ondi"]},
    },
    "MOOD": {
        "ko": {"GOOD": ["기분 좋으심", "웃으심", "밝으심"], "LOW": ["기운 없으심", "말수가 적으심", "우울해하심"], "AGITATED": ["화내심", "불안해하심", "초조해하심"]},
        "vi": {"GOOD": ["vui vẻ", "hay cười"], "LOW": ["buồn", "ít nói", "mệt mỏi"], "AGITATED": ["cáu gắt", "lo lắng", "bồn chồn"]},
        "ne": {"GOOD": ["खुसी", "हाँस्नुभयो"], "LOW": ["उदास", "कम बोल्नुभयो"], "AGITATED": ["रिसाउनुभयो", "छटपटाउनुभयो"]},
        "id": {"GOOD": ["senang", "tersenyum"], "LOW": ["sedih", "murung", "pendiam"], "AGITATED": ["gelisah", "marah", "cemas"]},
        "uz": {"GOOD": ["kayfiyati yaxshi", "kuldi"], "LOW": ["xafa", "tushkun", "kam gapirdi"], "AGITATED": ["jahli chiqdi", "bezovta", "xavotirlandi"]},
    },
    "EXCRETION": {
        "ko": {"NORMAL": ["대변 보심", "소변 보심", "배변함"], "NONE": ["대변 못 보심", "변 소식 없음", "배변 없음"], "LOOSE": ["설사하심", "묽은 변"]},
        "vi": {"NORMAL": ["đi vệ sinh bình thường", "đi đại tiện"], "NONE": ["chưa đi đại tiện", "chưa đi ngoài"], "LOOSE": ["tiêu chảy", "phân lỏng"]},
        "ne": {"NORMAL": ["दिसा गर्नुभयो"], "NONE": ["दिसा गर्नुभएन"], "LOOSE": ["पखाला", "पातलो दिसा"]},
        "id": {"NORMAL": ["sudah BAB", "buang air lancar"], "NONE": ["belum BAB", "tidak BAB"], "LOOSE": ["diare", "BAB cair"]},
        "uz": {"NORMAL": ["ichi keldi", "hojatxonaga bordi"], "NONE": ["ichi kelmadi"], "LOOSE": ["ichi ketdi", "ichi suyuq"]},
    },
    "EVENT": {
        "ko": {"FALL": ["넘어지심", "낙상", "바닥에 쓰러지심"], "NEAR_FALL": ["넘어질 뻔하심", "휘청하심", "휘청하셔서 잡아드림"]},
        "vi": {"FALL": ["bị ngã", "ngã"], "NEAR_FALL": ["suýt ngã", "loạng choạng"]},
        "ne": {"FALL": ["लड्नुभयो"], "NEAR_FALL": ["लड्न लाग्नुभयो", "लरखराउनुभयो"]},
        "id": {"FALL": ["jatuh", "terjatuh"], "NEAR_FALL": ["hampir jatuh", "sempoyongan"]},
        "uz": {"FALL": ["yiqildi", "yiqilib tushdi"], "NEAR_FALL": ["yiqilishiga oz qoldi", "gandiraklab ketdi"]},
    },
    "SUPPORT": {
        "ko": {"BATH": ["세면 도와드림", "목욕 도와드림", "샤워 지원"], "WALK": ["산책함", "부축해 드림", "이동 도와드림"], "DRESS": ["옷 갈아입혀 드림", "환복 지원"], "MEAL_ASSIST": ["식사 떠먹여 드림", "식사 보조함"], "CLEAN": ["청소함", "침구 정리함", "빨래함"], "REPOSITION": ["체위 바꿔드림", "체위 변경함", "자세 바꿔드림"]},
        "vi": {"BATH": ["giúp tắm", "lau người"], "WALK": ["đỡ đi", "dìu đi", "đỡ dậy"], "DRESS": ["thay quần áo"], "MEAL_ASSIST": ["đút ăn", "hỗ trợ ăn"], "CLEAN": ["dọn phòng", "giặt đồ"], "REPOSITION": ["trở mình", "đổi tư thế"]},
        "ne": {"BATH": ["नुहाउन सहयोग"], "WALK": ["हिँड्न सहयोग", "समातेर लगेँ"], "DRESS": ["लुगा फेर्न सहयोग"], "MEAL_ASSIST": ["खाना खुवाइदिएँ"], "CLEAN": ["कोठा सफा"], "REPOSITION": ["सुताइ फेरिदिएँ", "कोल्टे फेरिदिएँ"]},
        "id": {"BATH": ["bantu mandi", "seka badan"], "WALK": ["bantu jalan", "memapah"], "DRESS": ["bantu ganti baju", "ganti baju"], "MEAL_ASSIST": ["menyuapi", "bantu makan"], "CLEAN": ["bersihkan kamar", "rapikan tempat tidur"], "REPOSITION": ["ubah posisi", "miringkan badan"]},
        "uz": {"BATH": ["cho'miltirdim", "yuvintirdim"], "WALK": ["sayr qildik", "suyab bordim"], "DRESS": ["kiyim almashtirdim", "kiyintirdim"], "MEAL_ASSIST": ["ovqat yedirdim"], "CLEAN": ["xonani tozaladim"], "REPOSITION": ["holatini o'zgartirdim", "ag'dardim"]},
    },
}

# 한국어 현장 메모 축약체(음슴체) 변환 규칙: 학습 데이터 증강용
KO_SHORT = [("드셨습니다", "드심"), ("드셨어요", "드심"), ("하셨습니다", "하심"), ("하셨어요", "하심"), ("드렸습니다", "드림"), ("드렸어요", "드림"),
            ("했습니다", "함"), ("했어요", "함"), ("셨습니다", "심"), ("셨어요", "심"), ("습니다", "음"), ("어요", "음")]
