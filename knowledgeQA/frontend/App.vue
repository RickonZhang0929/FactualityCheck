<template>
  <div id="app">
    <h1>文件管理与问答系统</h1>

    <!-- 上传文件 -->
    <div>
      <h2>上传文件到知识库</h2>
      <form @submit.prevenat="uploadFile">
        <input type="file" @change="handleFileUpload" />
        <input type="text" v-model="knowledgeId" placeholder="知识库 ID" />
        <button type="submit">上传</button>
      </form>
    </div>

    <!-- 提问 -->
    <div>
      <h2>问答系统</h2>
      <input type="text" v-model="question" placeholder="输入问题" />
      <button @click="askQuestion">提问</button>
    </div>

    <div v-if="answer">
      <h3>答案</h3>
      <p>{{ answer }}</p>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  data() {
    return {
      selectedFile: null,
      knowledgeId: '',
      question: '',
      answer: null
    }
  },
  methods: {
    handleFileUpload(event) {
      this.selectedFile = event.target.files[0];
    },
    uploadFile() {
      const formData = new FormData();
      formData.append('file', this.selectedFile);
      formData.append('knowledge_id', this.knowledgeId);

      axios.post('http://localhost:5000/upload', formData)
        .then(response => {
          alert('文件上传成功');
        })
        .catch(error => {
          console.error(error);
        });
    },
    askQuestion() {
      axios.post('http://localhost:5000/ask', {
        question: this.question,
        knowledge_id: this.knowledgeId
      })
      .then(response => {
        this.answer = response.data.answer;
      })
      .catch(error => {
        console.error(error);
      });
    }
  }
}
</script>

<style scoped>
#app {
  font-family: Arial, sans-serif;
  margin: 20px;
}
</style>
