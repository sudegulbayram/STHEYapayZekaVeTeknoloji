"use client";

import { useState, useRef, useEffect } from "react";
import { Send, Paperclip, Bot, User, Activity, FileText, CheckCircle2, ChevronRight, LayoutDashboard, MessageSquare, Terminal, Lock, Mail, ShieldCheck, UserPlus, Users } from "lucide-react";

export default function Home() {
  const [activeTab, setActiveTab] = useState<"chat" | "admin" | "admin-register">("chat");
  const [isAdminAuthenticated, setIsAdminAuthenticated] = useState(false);
  const [showAuthModal, setShowAuthModal] = useState(false);
  
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  // Admin listesi (Panel içinden yeni admin eklenebilir)
  const [adminList, setAdminList] = useState<{ email: string; name: string; date: string }[]>([
    { email: "admin@bootcamp.com", name: "Sistem Yöneticisi", date: "2026-07-30" }
  ]);
  const [newAdminName, setNewAdminName] = useState("");
  const [newAdminEmail, setNewAdminEmail] = useState("");
  const [newAdminPassword, setNewAdminPassword] = useState("");

  const [message, setMessage] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [chat, setChat] = useState<{ sender: "user" | "ai"; text: string; file?: string }[]>([]);
  const [isTyping, setIsTyping] = useState(false);
  const [adminLogs, setAdminLogs] = useState<{ time: string; log: string; status: "loading" | "success" | "info" }[]>([]);
  
  const chatEndRef = useRef<HTMLDivElement>(null);
  const logsEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [chat, isTyping]);

  useEffect(() => {
    logsEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [adminLogs]);

  const addLog = (log: string, status: "loading" | "success" | "info" = "info") => {
    const time = new Date().toLocaleTimeString('tr-TR', { hour: '2-digit', minute: '2-digit', second:'2-digit' });
    setAdminLogs(prev => [...prev, { time, log, status }]);
  };

  const handleAdminAuth = (e: React.FormEvent) => {
    e.preventDefault();
    if (!email || !password) {
      alert("Lütfen e-posta ve şifre girin!");
      return;
    }
    setIsAdminAuthenticated(true);
    setShowAuthModal(false);
    setActiveTab("admin");
    addLog(`Admin girişi yapıldı: ${email}`, "success");
  };

  const handleCreateNewAdmin = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newAdminEmail || !newAdminPassword || !newAdminName) {
      alert("Lütfen tüm alanları doldurun!");
      return;
    }
    setAdminList(prev => [...prev, { email: newAdminEmail, name: newAdminName, date: new Date().toISOString().split('T')[0] }]);
    setNewAdminName("");
    setNewAdminEmail("");
    setNewAdminPassword("");
    alert("Yeni admin başarıyla eklendi!");
    addLog(`Yeni admin hesabı oluşturuldu: ${newAdminEmail}`, "success");
  };

  const handleTabSwitch = (tab: "chat" | "admin" | "admin-register") => {
    if ((tab === "admin" || tab === "admin-register") && !isAdminAuthenticated) {
      setShowAuthModal(true);
    } else {
      setActiveTab(tab);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
      addLog("Yeni dosya/resim seçildi: " + e.target.files[0].name, "info");
    }
  };

  const handleSendMessage = () => {
    if (!message && !file) return;

    const userMsg = message;
    const currentFile = file;
    
    setChat(prev => [...prev, { sender: "user", text: userMsg, file: currentFile?.name }]);
    setMessage("");
    setFile(null);
    setIsTyping(true);

    addLog("Kullanıcı promptu işlendi...", "info");
    
    setTimeout(() => {
      addLog("OCR / Görüntü işleme katmanı çalıştırılıyor...", "loading");
    }, 600);

    setTimeout(() => {
      addLog("RAG Pipeline: Metin chunk'lara bölünüp FAISS vektör indeksinde aranıyor...", "loading");
    }, 1400);

    setTimeout(() => {
      addLog("DeepSeek API: Sistem promptu ve bulunan bağlam birleştirilerek modele gönderildi...", "loading");
    }, 2400);

    setTimeout(() => {
      addLog("Model yanıtı başarıyla oluşturuldu ve kullanıcıya iletildi.", "success");
      setChat(prev => [...prev, { 
        sender: "ai", 
        text: "Yüklediğiniz veriyi ve metni DeepSeek & RAG altyapısı ile analiz ettim. Hukuki ve teknik bağlama göre sistem yanıtı hazırlandı." 
      }]);
      setIsTyping(false);
    }, 3500);
  };

  return (
    <div className="flex h-screen bg-slate-900 font-sans overflow-hidden relative">
      
      {/* SOL MENÜ */}
      <div className="w-64 bg-slate-950 border-r border-slate-800 flex flex-col justify-between p-4 z-20">
        <div>
          <div className="flex items-center gap-3 px-3 py-4 mb-6 border-b border-slate-800">
            <div className="w-9 h-9 bg-blue-600 rounded-xl flex items-center justify-center shadow-lg shadow-blue-500/30">
              <Bot className="text-white w-5 h-5" />
            </div>
            <div>
              <h2 className="font-bold text-slate-100 text-sm">YZVT Bootcamp</h2>
              <p className="text-[11px] text-slate-400">Legal AI Assistant</p>
            </div>
          </div>

          <nav className="space-y-2">
            <button 
              onClick={() => handleTabSwitch("chat")}
              className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium transition-all cursor-pointer ${
                activeTab === "chat" 
                  ? "bg-blue-600 text-white shadow-lg shadow-blue-600/20" 
                  : "text-slate-400 hover:bg-slate-900 hover:text-slate-200"
              }`}
            >
              <MessageSquare className="w-4 h-4" />
              Chat & Analiz Ekranı
            </button>

            <button 
              onClick={() => handleTabSwitch("admin")}
              className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium transition-all cursor-pointer ${
                activeTab === "admin" 
                  ? "bg-blue-600 text-white shadow-lg shadow-blue-600/20" 
                  : "text-slate-400 hover:bg-slate-900 hover:text-slate-200"
              }`}
            >
              <LayoutDashboard className="w-4 h-4" />
              Admin Paneli
              {!isAdminAuthenticated && <span className="ml-auto text-[10px] bg-slate-800 text-slate-400 px-1.5 py-0.5 rounded">Kilitli</span>}
            </button>

            {isAdminAuthenticated && (
              <button 
                onClick={() => handleTabSwitch("admin-register")}
                className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium transition-all cursor-pointer ${
                  activeTab === "admin-register" 
                    ? "bg-blue-600 text-white shadow-lg shadow-blue-600/20" 
                    : "text-slate-400 hover:bg-slate-900 hover:text-slate-200"
                }`}
              >
                <UserPlus className="w-4 h-4" />
                Yeni Admin Ekle
              </button>
            )}
          </nav>
        </div>

        <div className="space-y-2 border-t border-slate-800/80 pt-3">
          {isAdminAuthenticated && (
            <div className="text-[11px] text-slate-400 px-2 truncate">
              Oturum: <span className="text-green-400 font-medium">{email}</span>
            </div>
          )}
          <div className="text-xs text-slate-500 px-2 flex items-center justify-between">
            <span>Sistem: <span className="text-green-400 font-semibold">Aktif</span></span>
            {isAdminAuthenticated && (
              <button onClick={() => { setIsAdminAuthenticated(false); setActiveTab("chat"); }} className="text-red-400 hover:text-red-300 text-[11px] cursor-pointer">Çıkış</button>
            )}
          </div>
        </div>
      </div>

      {/* SAĞ İÇERİK ALANI */}
      <div className="flex-1 flex flex-col bg-slate-50 overflow-hidden relative">
        
        {activeTab === "chat" && (
          <div className="flex-1 flex flex-col h-full bg-white">
            <div className="h-16 border-b border-slate-200 flex items-center px-8 bg-white justify-between">
              <h1 className="font-bold text-slate-800 text-lg">Yapay Zeka Sohbet ve Belge/Resim Analizi</h1>
              <span className="text-xs bg-blue-50 text-blue-600 px-3 py-1 rounded-full font-medium border border-blue-100">DeepSeek & RAG Entegre</span>
            </div>

            <div className="flex-1 overflow-y-auto p-8 space-y-6 bg-slate-50/50">
              {chat.length === 0 ? (
                <div className="h-full flex flex-col items-center justify-center text-slate-400">
                  <Bot className="w-16 h-16 mb-3 text-slate-300 animate-bounce" />
                  <p className="text-base font-medium text-slate-600">Herkese Açık Asistan: Belge veya resim yükleyip soru sorabilirsiniz.</p>
                  <p className="text-xs text-slate-400 mt-1">PDF, PNG, JPG, TXT formatları desteklenir.</p>
                </div>
              ) : (
                chat.map((msg, index) => (
                  <div key={index} className={`flex gap-4 ${msg.sender === "user" ? "flex-row-reverse" : "flex-row"}`}>
                    <div className={`w-9 h-9 rounded-full flex items-center justify-center shrink-0 ${msg.sender === "user" ? "bg-slate-800" : "bg-blue-600"}`}>
                      {msg.sender === "user" ? <User className="text-white w-4 h-4" /> : <Bot className="text-white w-4 h-4" />}
                    </div>
                    <div className={`max-w-[70%] flex flex-col gap-2 ${msg.sender === "user" ? "items-end" : "items-start"}`}>
                      {msg.file && (
                        <div className="bg-blue-50 border border-blue-100 px-3 py-1.5 rounded-lg flex items-center gap-2 text-xs text-blue-700">
                          <FileText className="w-3.5 h-3.5" />
                          {msg.file}
                        </div>
                      )}
                      {msg.text && (
                        <div className={`px-4 py-3 rounded-2xl shadow-sm text-sm leading-relaxed ${
                          msg.sender === "user" 
                            ? "bg-slate-800 text-white rounded-tr-none" 
                            : "bg-white border border-slate-200 text-slate-700 rounded-tl-none"
                        }`}>
                          {msg.text}
                        </div>
                      )}
                    </div>
                  </div>
                ))
              )}
              
              {isTyping && (
                <div className="flex gap-4 items-center">
                  <div className="w-9 h-9 bg-blue-600 rounded-full flex items-center justify-center">
                    <Bot className="text-white w-4 h-4" />
                  </div>
                  <div className="bg-white border border-slate-200 px-4 py-3 rounded-2xl rounded-tl-none flex gap-1.5 shadow-sm">
                    <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce"></div>
                    <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: "0.2s" }}></div>
                    <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: "0.4s" }}></div>
                  </div>
                </div>
              )}
              <div ref={chatEndRef} />
            </div>

            <div className="p-6 bg-white border-t border-slate-200">
              {file && (
                <div className="mb-2 flex items-center gap-2 text-xs text-blue-600 bg-blue-50 w-fit px-3 py-1 rounded-md border border-blue-100">
                  <FileText className="w-3.5 h-3.5" /> {file.name} seçildi.
                </div>
              )}
              <div className="flex items-center gap-3 bg-slate-50 border border-slate-200 rounded-xl p-2 pr-3 focus-within:border-blue-500 focus-within:ring-2 focus-within:ring-blue-100 transition-all">
                <label className="cursor-pointer p-2.5 hover:bg-slate-200 rounded-lg text-slate-500 transition-colors" title="Dosya veya Resim Yükle">
                  <Paperclip className="w-5 h-5" />
                  <input type="file" onChange={handleFileChange} className="hidden" accept="image/*,.pdf,.txt" />
                </label>
                <input 
                  type="text" 
                  value={message}
                  onChange={(e) => setMessage(e.target.value)}
                  placeholder="Yapay zekaya bir soru sorun veya belge/resim analizi isteyin..."
                  className="flex-1 bg-transparent border-none focus:outline-none text-slate-800 text-sm px-2"
                  onKeyDown={(e) => e.key === 'Enter' && handleSendMessage()}
                />
                <button 
                  onClick={handleSendMessage}
                  className="bg-blue-600 text-white p-2.5 rounded-lg hover:bg-blue-700 transition-colors shadow-sm cursor-pointer"
                >
                  <Send className="w-4 h-4" />
                </button>
              </div>
            </div>
          </div>
        )}

        {activeTab === "admin" && isAdminAuthenticated && (
          <div className="flex-1 flex flex-col h-full bg-slate-900 text-slate-100 p-8 overflow-y-auto">
            <div className="flex items-center justify-between border-b border-slate-800 pb-4 mb-6">
              <div className="flex items-center gap-3">
                <Terminal className="w-6 h-6 text-green-400" />
                <h1 className="text-xl font-bold">Admin Paneli & Prompt Düşünce Süreci (CoT)</h1>
              </div>
              <span className="text-xs bg-green-500/10 text-green-400 border border-green-500/20 px-3 py-1 rounded-full flex items-center gap-1">
                <ShieldCheck className="w-3.5 h-3.5" /> Yetkili Oturum Açık
              </span>
            </div>

            <div className="grid grid-cols-3 gap-6 mb-8">
              <div className="bg-slate-950 p-5 rounded-2xl border border-slate-800">
                <p className="text-xs text-slate-400 mb-1">Toplam Sorgu</p>
                <h3 className="text-2xl font-bold text-blue-400">1,248</h3>
              </div>
              <div className="bg-slate-950 p-5 rounded-2xl border border-slate-800">
                <p className="text-xs text-slate-400 mb-1">Aktif Model</p>
                <h3 className="text-2xl font-bold text-purple-400">DeepSeek-V3 / RAG</h3>
              </div>
              <div className="bg-slate-950 p-5 rounded-2xl border border-slate-800">
                <p className="text-xs text-slate-400 mb-1">Kayıtlı Adminler</p>
                <h3 className="text-2xl font-bold text-green-400">{adminList.length} Kişi</h3>
              </div>
            </div>

            <h2 className="text-sm font-semibold text-slate-300 mb-3 flex items-center gap-2">
              <Activity className="w-4 h-4 text-blue-400" /> Arka Plan Prompt ve Model Düşünce Logları (Chain of Thought)
            </h2>
            
            <div className="flex-1 bg-slate-950 border border-slate-800 rounded-2xl p-6 font-mono text-xs space-y-4 overflow-y-auto min-h-[300px]">
              <div className="text-slate-500">
                <span className="text-blue-400">root@yzvt-bootcamp:~#</span> tail -f /var/log/deepseek_rag_pipeline.log<br/>
                [SYSTEM]: Admin paneli yetkilendirildi. Model ve prompt zinciri izleniyor...
              </div>

              {adminLogs.length === 0 ? (
                <div className="text-slate-600 italic mt-4">Henüz bir prompt isteği gönderilmedi. Chat ekranından mesaj attığınızda loglar burada görünecektir.</div>
              ) : (
                adminLogs.map((log, i) => (
                  <div key={i} className="flex flex-col gap-1 border-l-2 border-slate-800 pl-3 py-1">
                    <div className="text-slate-500 text-[11px] flex items-center gap-1">
                      <ChevronRight className="w-3 h-3 text-slate-600" /> {log.time}
                    </div>
                    <div className={`flex items-start gap-2 ${
                      log.status === "loading" ? "text-yellow-400" : 
                      log.status === "success" ? "text-green-400" : "text-blue-300"
                    }`}>
                      {log.status === "success" && <CheckCircle2 className="w-4 h-4 mt-0.5 shrink-0" />}
                      {log.status === "loading" && <div className="w-4 h-4 mt-0.5 border-2 border-yellow-400 border-t-transparent rounded-full animate-spin shrink-0" />}
                      {log.status === "info" && <div className="text-blue-400 font-bold shrink-0">{">"}</div>}
                      <span>{log.log}</span>
                    </div>
                  </div>
                ))
              )}
              <div ref={logsEndRef} />
            </div>
          </div>
        )}

        {activeTab === "admin-register" && isAdminAuthenticated && (
          <div className="flex-1 flex flex-col h-full bg-slate-900 text-slate-100 p-8 overflow-y-auto">
            <div className="flex items-center justify-between border-b border-slate-800 pb-4 mb-6">
              <div className="flex items-center gap-3">
                <UserPlus className="w-6 h-6 text-blue-400" />
                <h1 className="text-xl font-bold">Yeni Admin Ekleme ve Yetkilendirme</h1>
              </div>
              <span className="text-xs bg-blue-500/10 text-blue-400 border border-blue-500/20 px-3 py-1 rounded-full flex items-center gap-1">
                <Users className="w-3.5 h-3.5" /> Yönetici Modülü
              </span>
            </div>

            <div className="grid grid-cols-2 gap-8">
              {/* Form Alanı */}
              <div className="bg-slate-950 border border-slate-800 rounded-2xl p-6 shadow-xl">
                <h2 className="text-sm font-semibold text-slate-200 mb-4">Yeni Yetkili Admin Kaydı Oluştur</h2>
                <form onSubmit={handleCreateNewAdmin} className="space-y-4">
                  <div>
                    <label className="block text-xs font-medium text-slate-400 mb-1">Ad Soyad</label>
                    <input 
                      type="text" 
                      value={newAdminName}
                      onChange={(e) => setNewAdminName(e.target.value)}
                      placeholder="Örn: Sude Gül Bayram"
                      className="w-full bg-slate-900 border border-slate-800 rounded-xl px-4 py-3 text-sm text-slate-200 focus:outline-none focus:border-blue-500"
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-slate-400 mb-1">E-posta Adresi</label>
                    <input 
                      type="email" 
                      value={newAdminEmail}
                      onChange={(e) => setNewAdminEmail(e.target.value)}
                      placeholder="admin@sirket.com"
                      className="w-full bg-slate-900 border border-slate-800 rounded-xl px-4 py-3 text-sm text-slate-200 focus:outline-none focus:border-blue-500"
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-slate-400 mb-1">Geçici Şifre</label>
                    <input 
                      type="password" 
                      value={newAdminPassword}
                      onChange={(e) => setNewAdminPassword(e.target.value)}
                      placeholder="••••••••"
                      className="w-full bg-slate-900 border border-slate-800 rounded-xl px-4 py-3 text-sm text-slate-200 focus:outline-none focus:border-blue-500"
                      required
                    />
                  </div>
                  <button 
                    type="submit"
                    className="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-3 rounded-xl transition-colors shadow-lg shadow-blue-600/30 text-sm cursor-pointer"
                  >
                    Sisteme Yeni Admin Kaydet
                  </button>
                </form>
              </div>

              {/* Mevcut Adminler Listesi */}
              <div className="bg-slate-950 border border-slate-800 rounded-2xl p-6 shadow-xl flex flex-col">
                <h2 className="text-sm font-semibold text-slate-200 mb-4">Sistemdeki Aktif Adminler ({adminList.length})</h2>
                <div className="space-y-3 flex-1 overflow-y-auto">
                  {adminList.map((adm, idx) => (
                    <div key={idx} className="bg-slate-900 border border-slate-800 p-3.5 rounded-xl flex items-center justify-between">
                      <div>
                        <p className="text-sm font-medium text-slate-200">{adm.name}</p>
                        <p className="text-xs text-slate-400">{adm.email}</p>
                      </div>
                      <span className="text-[10px] bg-green-500/10 text-green-400 px-2 py-1 rounded-md border border-green-500/20">Yetkili</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}

      </div>

      {/* GİRİŞ MODALI */}
      {showAuthModal && (
        <div className="fixed inset-0 bg-slate-950/80 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <div className="w-full max-w-md bg-slate-900 border border-slate-800 rounded-3xl p-8 shadow-2xl animate-in fade-in zoom-in-95 duration-200">
            <div className="flex flex-col items-center mb-6">
              <div className="w-12 h-12 bg-blue-600 rounded-2xl flex items-center justify-center shadow-lg shadow-blue-500/30 mb-3">
                <Lock className="text-white w-6 h-6" />
              </div>
              <h1 className="text-xl font-bold text-slate-100">Admin Paneli Korumalı</h1>
              <p className="text-xs text-slate-400 mt-1">Bu alana erişmek için yönetici girişi yapın.</p>
            </div>

            <form onSubmit={handleAdminAuth} className="space-y-4">
              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1">Admin E-posta</label>
                <div className="flex items-center bg-slate-950 border border-slate-800 rounded-xl px-3 focus-within:border-blue-500">
                  <Mail className="w-4 h-4 text-slate-500 mr-2" />
                  <input 
                    type="email" 
                    value={email} 
                    onChange={(e) => setEmail(e.target.value)} 
                    placeholder="admin@bootcamp.com"
                    className="w-full bg-transparent py-3 text-sm text-slate-200 focus:outline-none"
                    required
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1">Şifre</label>
                <div className="flex items-center bg-slate-950 border border-slate-800 rounded-xl px-3 focus-within:border-blue-500">
                  <Lock className="w-4 h-4 text-slate-500 mr-2" />
                  <input 
                    type="password" 
                    value={password} 
                    onChange={(e) => setPassword(e.target.value)} 
                    placeholder="••••••••"
                    className="w-full bg-transparent py-3 text-sm text-slate-200 focus:outline-none"
                    required
                  />
                </div>
              </div>

              <div className="flex gap-3 pt-2">
                <button 
                  type="button"
                  onClick={() => setShowAuthModal(false)}
                  className="flex-1 bg-slate-800 hover:bg-slate-700 text-slate-300 font-medium py-3 rounded-xl transition-colors text-sm cursor-pointer"
                >
                  Vazgeç / Chat'e Dön
                </button>
                <button 
                  type="submit"
                  className="flex-1 bg-blue-600 hover:bg-blue-700 text-white font-medium py-3 rounded-xl transition-colors shadow-lg shadow-blue-600/30 text-sm cursor-pointer"
                >
                  Giriş Yap
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

    </div>
  );
}