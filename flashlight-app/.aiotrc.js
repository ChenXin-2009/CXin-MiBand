module.exports = {
  // 项目配置
  projectConfig: {
    // 项目名称
    projectName: 'vela-test-app',
    // 源码目录
    source: 'src',
    // 输出目录
    output: 'dist',
    // 构建目录
    build: 'build'
  },
  
  // 编译配置
  compilerConfig: {
    // 是否压缩代码
    minify: false,
    // 是否生成 sourcemap
    sourceMap: true
  },
  
  // 服务器配置
  serverConfig: {
    // 开发服务器端口
    port: 8080,
    // 是否自动打开浏览器
    open: false
  }
};
